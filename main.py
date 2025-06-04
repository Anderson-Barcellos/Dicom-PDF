from DicomManager.unzip import Unzipper
from DicomManager.DICOM import DICOM2JPEG
import os
from reportlab.platypus import Image as rlImage
from reportlab.lib import colors
from PDFMAKER.pdfmaker import MkPDF
import time
from utils.ocr import extract_ultrasound_text

from extract_ultrasound_text import extract_ultrasound_text

from utils.ocr import extract_ultrasound_text


import win32print
import win32api

def sleep_with_while(seconds):
    start_time = time.time()  # Tempo inicial
    while time.time() - start_time < seconds:
        elapsed_time = time.time() - start_time
        remaining_time = seconds - elapsed_time
        print(f"Faltam {int(remaining_time)} segundos...")
        time.sleep(1)  # Aguardar um segundo entre cada iteração
    print("Tempo finalizado!")



def imprimir_arquivo(path_arquivo, nome_impressora="EPSON L3250 Series"):
    # Verifica se o arquivo especificado existe
    if not os.path.exists(path_arquivo):
        print(f"Arquivo não encontrado: {path_arquivo}")
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
        print(f"Arquivo {path_arquivo} enviado para a impressora {nome_impressora}.")
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
    print(name)
    dicom2jpeg = DICOM2JPEG("./Dicoms", "./Images")
    dicom2jpeg.converter()

    # Realiza OCR nas imagens convertidas antes de removê-las
    os.makedirs("Pacientes", exist_ok=True)
    txt_path = os.path.join("Pacientes", f"{name[15:]}.txt")
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        for img in os.listdir("./Images"):
            if img.lower().endswith(('.jpeg', '.jpg', '.png', '.bmp')):
                img_path = os.path.join("./Images", img)
                text, _ = extract_ultrasound_text(img_path)
                txt_file.write(f"# {img}\n{text}\n")

    MkPDF(name)
    dicom2jpeg.eliminate_all()

    return f"{name}.pdf"[15:]

        
    #Test for a any other pdf file on the current folder

    print("Extração e conversão concluídas com sucesso, Anders!")



# ORTHANC
from pyorthanc import Orthanc
import time
import json



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
