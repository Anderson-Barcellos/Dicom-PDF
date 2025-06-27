import json
import os
import time
from pyorthanc import Orthanc
from DicomManager.unzip import Unzipper
from DicomManager.DICOM import DICOM2JPEG
from PDFMAKER.pdfmaker import MkPDF


from utils.ocr import extract_ultrasound_text

from utils.gpt_client import GPTClient




# Windows-specific imports - only available on Windows
try:
    import win32print
    import win32api
    WINDOWS_PRINTING_AVAILABLE = True
except ImportError:
    # Not on Windows or pywin32 not installed
    WINDOWS_PRINTING_AVAILABLE = False


def sleep_with_while(seconds):
    start_time = time.time()  # Tempo inicial
    while time.time() - start_time < seconds:
        elapsed_time = time.time() - start_time
        remaining_time = seconds - elapsed_time
        print(f"Faltam {int(remaining_time)} segundos...")
        time.sleep(1)  # Aguardar um segundo entre cada iteração
    print("Tempo finalizado!")


def imprimir_arquivo(path_arquivo, nome_impressora="EPSON L3250 Series"):
    """
    🖨️ Função de Impressão de Arquivo

    Função para enviar um arquivo para impressão em uma impressora específica no Windows.

    📥 Parâmetros:
    :param path_arquivo: 📄 Caminho do arquivo a ser impresso.
    :type path_arquivo: str
    :param nome_impressora: 🖨️ Nome da impressora a ser utilizada. Se None, utiliza a impressora padrão.
    :type nome_impressora: str, optional

    :return: None

    :raises FileNotFoundError: ❌ Se o arquivo especificado não for encontrado.
    :raises Exception: ⚠️ Se ocorrer um erro ao enviar o arquivo para a impressora.

    🧑‍💻 Exemplo:
    ```python

        imprimir_arquivo("relatorio.pdf")
        imprimir_arquivo("imagem.jpg", nome_impressora="Minha Impressora")
    ```

    """
    if not os.path.exists(path_arquivo):
        print(f"Arquivo não encontrado: {path_arquivo}")
        return

    # Check if Windows printing is available
    if not WINDOWS_PRINTING_AVAILABLE:
        print(f"⚠️ Impressão não disponível nesta plataforma. Arquivo: {path_arquivo}")
        print("💡 A funcionalidade de impressão está disponível apenas no Windows.")
        return

    # Obtém a impressora padrão se nenhuma impressora for especificada
    if nome_impressora is None:
        nome_impressora = win32print.GetDefaultPrinter()

    # Envia o arquivo para a impressora
    try:
        win32api.ShellExecute(
            0,
            "print",
            path_arquivo,
            f'"{nome_impressora}"',
            ".",
            0
        )
        print(
            f"Arquivo {path_arquivo} enviado para a impressora {nome_impressora}.")
    except Exception as e:
        print(f"Erro ao imprimir o arquivo: {e}")


def Extract_Convert_Img(file: str):
    """Extrai imagens DICOM, converte-as e gera relatórios.

    Parameters
    ----------
    file : str
        Nome do arquivo ZIP que contém as imagens DICOM.

    Returns
    -------
    str
        Caminho do PDF criado a partir das imagens. Após sua geração, um
        processo de OCR pode ser executado para criar o arquivo de texto
        correspondente.
    """
    # Extract the file
    unzipper = Unzipper(f"{file}", "./Dicoms")
    unzipper.unzipper()
    name = unzipper.name
    patient_name = name[15:]
    print(name)

    # create patient folders
    base_dir = os.path.join("Pacientes", patient_name)
    images_dir = os.path.join(base_dir, "IMAGENS")
    docs_dir = os.path.join(base_dir, "DOCUMENTOS")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)

    dicom2jpeg = DICOM2JPEG("./Dicoms", images_dir)
    dicom2jpeg.converter()

    gpt = GPTClient()

    # OCR das imagens convertidas com melhoria via GPT
    txt_path = os.path.join(docs_dir, f"{patient_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        for img in os.listdir(images_dir):
            if img.lower().endswith((".jpeg", ".jpg", ".png", ".bmp")):
                img_path = os.path.join(images_dir, img)
                text, _ = extract_ultrasound_text(img_path)
                enhanced_lines = []
                for line in text.splitlines():
                    if line.strip():
                        enhanced_lines.append(gpt.enhance_text(line))
                    else:
                        enhanced_lines.append("")
                txt_file.write(f"# {img}\n" + "\n".join(enhanced_lines) + "\n")

    MkPDF(name, images_dir, docs_dir)
    dicom2jpeg.eliminate_dcm()

    return os.path.join(docs_dir, f"{patient_name}.pdf")

    # Test for a any other pdf file on the current folder

    print("Extração e conversão concluídas com sucesso, Anders!")


# ORTHANC


orthanc = Orthanc("", "orthanc", "orthanc")
try:
    while True:
        # Load pacientes atualizados
        patients = None
        with open('patients.json') as json_file:
            patients = json.load(json_file)

        # Atualização os pacientes
        latest_patients = orthanc.get_patients()
        if patients == latest_patients:
            print("Nenhum novo paciente encontrado, Anders.... Procurando")
            sleep_with_while(20)
        else:
            new_patients = [p for p in latest_patients if p not in patients]

            # Processo para cada novo paciente
            for patient in new_patients:
                response = orthanc.get_patients_id_archive(str(patient))
                with open(f"ZIPS/{patient}.zip", "wb") as f:
                    f.write(response)
                imprimir_arquivo(Extract_Convert_Img(f"{patient}.zip"))

            # Atualizar pacientes
            patients = latest_patients

            with open('patients.json', 'w') as json_file:
                json.dump(patients, json_file)

            # Esperar um momento (tempo em segundos) antes de verificar novamente
            sleep_with_while(15)
except Exception as e:
    print(e)
