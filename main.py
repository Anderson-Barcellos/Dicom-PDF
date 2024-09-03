from DicomManager.unzip import Unzipper
from DicomManager.DICOM import DICOM2JPEG
import os
from reportlab.platypus import Image as rlImage
from reportlab.lib import colors
from PDFMAKER.pdfmaker import MkPDF
from PyPDF2 import PdfMerger

path = "C:\\Users\\Administrador\\Desktop\\NEWDICOM\\Pacientes"

def Merger(path:str):
    print("Analisando PDFs...")
    path = path
    try:
        prefixes = set()
        pdf_pairs = []

        # Identificar os prefixos dos arquivos
        for file in os.listdir(path):
            if " " in file:
                prefix = file.split(" ")[0]
                prefixes.add(prefix)

        # Verificar se os arquivos de cada prefixo existem
        for prefix in prefixes:
            pdf1 = f"{prefix}.pdf"
            pdf2 = None
            for file in os.listdir(path):
                if file.startswith(prefix) and " " in file:
                    pdf2 = file
                    break
            if (
                pdf2
                and os.path.exists(os.path.join(path, pdf1))
                and os.path.exists(os.path.join(path, pdf2))
            ):
                pdf_pairs.append((pdf1, pdf2))

        # Realizar a fusão dos arquivos PDF
        for pdf1, pdf2 in pdf_pairs:
            if os.path.exists(f"Laudo_{pdf2[:-4]}.pdf"):
                print("Nada a unir!")
                continue
            else:
                output_filename = f"Laudo_{pdf2[:-4]}.pdf"
                merger = PdfMerger()
                merger.append(os.path.join(path, pdf1))
                merger.append(os.path.join(path, pdf2))
                merger.write(output_filename)
                merger.close()

            print("PDFs Unidos!")
    except Exception as e:
        print(e)


def Extract_Convert_Img(file: str):
    """Function to extract and convert DICOM images to JPEG format.
    #### Parameters:
    - file: str
        Name of the ZIP file containing the DICOM images."""
    # Extract the file
    unzipper = Unzipper(f"{file}", "./Dicoms")
    unzipper.unzipper()
    name = unzipper.name
    print(name)
    dicom2jpeg = DICOM2JPEG("./Dicoms", "./Images")
    dicom2jpeg.converter()
    MkPDF(name)
    dicom2jpeg.eliminate_folders()
    # Test for a any other pdf file on the current folder

    print("Extração e conversão concluídas com sucesso!")


def ExtractSR(file: str):
    """Function to extract and convert DICOM images to JPEG format.
    #### Parameters:
    - file: str
        Name of the ZIP file containing the DICOM images."""
    # Extract the file
    unzipper = Unzipper(f"{file}", "./Dicoms")
    unzipper.unzipper()
    name = unzipper.name
    print(name)
    dicom2jpeg = DICOM2JPEG("./Dicoms", "./Images")
    dicom2jpeg.converter()
    MkPDF(name)
    dicom2jpeg.eliminate_folders()
    # Test for a any other pdf file on the current folder

    print("Extração e conversão concluídas com sucesso!")


# ORTHANC
from pyorthanc import Orthanc
import time
import json

orthanc = Orthanc("http://170.238.45.149:8042", "orthanc", "orthanc")


def connection():
    max_attempts = 5  # Número máximo de tentativas antes de abortar
    attempt = 0
    while True:
        try:
            while True:
                # Load pacientes atualizados
                patients = None
                with open("patients.json") as json_file:
                    patients = json.load(json_file)

                # Atualização os pacientes
                latest_patients = orthanc.get_patients()

                if patients == latest_patients:
                    print("Nenhum novo paciente encontrado")
                    Merger(path)
                    time.sleep(15)
                else:
                    new_patients = [p for p in latest_patients if p not in patients]

                    # Processo para cada novo paciente
                    for patient in new_patients:

                        response = orthanc.get_patients_id_archive(str(patient))
                        print(f"Baixando paciente {patient}...")
                        with open(f"ZIPS/{patient}.zip", "wb") as f:
                            f.write(response)
                        Extract_Convert_Img(f"{patient}.zip")

                    # Atualizar pacientes
                    patients = latest_patients

                    with open("patients.json", "w") as json_file:
                        json.dump(patients, json_file)

                    # Esperar um momento (tempo em segundos) antes de verificar novamente
                    time.sleep(15)
        except Exception as e:
            attempt += 1
            print(f"Ocorreu um erro: {e}. Tentativa {attempt} de {max_attempts}")
            if attempt >= max_attempts:
                print("Número máximo de tentativas atingido. Abortando.")

                break
            else:
                connection()
                time.sleep(5)  # Pequeno delay antes de tentar novamente


connection()
