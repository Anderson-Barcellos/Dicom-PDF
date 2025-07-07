import json
import os
import time
from pyorthanc import Orthanc
from DicomManager.unzip import Unzipper
from DicomManager.DICOM import DICOM2JPEG
from PDFMAKER.pdfmaker import MkPDF


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

    # Get the default printer if no printer is specified
    if nome_impressora is None:
        nome_impressora = win32print.GetDefaultPrinter()

    # Send the file to the printer
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
    """
    🖼️ Extract_Convert_Img
    Extracts DICOM images from a ZIP file, converts them to JPEG format, and generates a PDF report. This function is part of a medical imaging workflow, facilitating the conversion and compilation of DICOM images for further analysis and reporting.

    ### 🖥️ Parameters
    - `file` (`str`): The name of the ZIP file containing DICOM images. The file should be located in the current working directory.

    ### 🔄 Returns
    - `str`: The path to the created PDF file. After its generation, an OCR process can be executed to create the corresponding text file.

    ### ⚠️ Raises
    - `FileNotFoundError`: If the specified ZIP file does not exist.
    - `OSError`: If there is an error during the extraction or conversion process.

    ### 💡 Example

    >>> Extract_Convert_Img("patient_data.zip")
    'Pacientes/Anders/Report/Anders.pdf'
    """
    # Extract the file
    unzipper = Unzipper(f"{file}", "Dicoms")
    # Unzip the file
    unzipper.unzipper()
    # Get the name of the patient
    name = unzipper.name[15:]
    print(name)

    # Create patient folders
    base_dir = os.path.join("Patients", name)
    images_dir = os.path.join(base_dir, "Images")
    reports_dir = os.path.join(base_dir, "Report")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    dicom2jpeg = DICOM2JPEG("./Dicoms", images_dir)
    dicom2jpeg.converter()

    # Generate the PDF
    MkPDF(name)
    dicom2jpeg.eliminate_dcm()

    return os.path.join(reports_dir, f"{name}.pdf")

    



# ORTHANC

def orthanc():
    orthanc = Orthanc("https://ultrassom.ai", "anders", "andi110386")
    try:
        while True:
            # Load pacientes with ZIPS folder
            oldest_patients = [patient[:-4] for patient in os.listdir("ZIPS")]
            print(oldest_patients)


            # Update patients
            latest_patients = orthanc.get_patients()
            if oldest_patients == latest_patients:
                print("Nenhum novo paciente encontrado, Anders.... Procurando")
                sleep_with_while(20)
            else:
                new_patients = [p for p in latest_patients if p not in oldest_patients]

                # Process for each new patient
                for patient in new_patients:
                    response = orthanc.get_patients_id_archive(str(patient))
                    with open(f"ZIPS/{patient}.zip", "wb") as f:
                        f.write(response)
                    Extract_Convert_Img(f"{patient}.zip")

                # Update patients            # Wait a moment (seconds) before checking again
                sleep_with_while(10)
    except Exception as e:
        print(e)
orthanc()
