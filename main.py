from DicomManager.unzip import Unzipper
from DicomManager.DICOM import DICOM2JPEG
from PDFMAKER.pdfmaker import MkPDF
import os
import PyPDF2

import glob

# ORTHANC
from pyorthanc import Orthanc

orthanc = Orthanc("http://usview.tech:8042", "orthanc", "orthanc")

def Down_All():
    patients = orthanc.get_patients()
    for patient in patients:
        print(patient)
        response = orthanc.get_patients_id_archive(str(patient))
        with open(f"ZIPS/{patient}.zip", "wb") as f:
            f.write(response)


# Donnload one patient
def Down_One(id):
    response = orthanc.get_patients_id_archive(id)
    with open(f"ZIPS/{id}.zip", "wb") as f:
        f.write(response)


def Change():
    get = orthanc.get_patients()

    id = f"{get[0]}"
    """p_changes = None
    with open("last_change.txt", "r") as f:
        p_changes = str(f.read())
    if p_changes == id or p_changes == "":
        with open("last_change.txt", "w") as f:
            f.write(id)
        print("No changes")
    else:
        with open("last_change.txt", "w") as f:
            f.write(id)"""
    print("Changes")
    Down_All()
    print("Done")


def PDFMerger(output_filename="merged_document.pdf"):
    """
    Procura por todos os arquivos PDF na pasta atual e os une em um único arquivo PDF.

    :param output_filename: Nome do arquivo de saída.
    """
    pdf_files = sorted(glob.glob("*.pdf"))
    if not pdf_files:
        print("Nenhum arquivo PDF encontrado na pasta.")
        return

    pdf_writer = PyPDF2.PdfWriter()  # Atualizado para PdfWriter

    for pdf_file in pdf_files:
        try:
            with open(pdf_file, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in pdf_reader.pages:
                    pdf_writer.add_page(page_num)
                    # Atualizado para add_page
        except Exception as e:
            print(f"Erro ao processar o arquivo {pdf_file}: {e}")
            continue

    with open(output_filename, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

    print(f"PDFs unidos com sucesso em {output_filename}.")


def check_folder():
    try:
        if not os.path.exists("Dicoms"):
            os.mkdir("Dicoms")
            print("Pasta criada DICOM criada com sucesso!")
        else:
            print("Pasta DICOM já existe!")
        if not os.path.exists("Images"):
            os.mkdir("Images")
            print("Pasta criada jpeg criada com sucesso!")
        else:
            print("Pasta jpeg já existe!")
    except Exception as e:
        print(e)


def Extract_Convert_Img(file: str):
    # Extract the file
    unzipper = Unzipper(f"{file}", "./Dicoms")
    unzipper.unzipper()
    name = unzipper.name
    print(name)
    dicom2jpeg = DICOM2JPEG("./Dicoms", "./Images")
    dicom2jpeg.converter()
    MkPDF(name)
    dicom2jpeg.eliminate_folders()
    #Test for a any other pdf file on the current folder

    print("Extração e conversão concluídas com sucesso!")


def PDF_Process():
    try:
        for file in os.listdir("ZIPS"):
            print(file)
            if file.endswith(".zip"):
                Extract_Convert_Img(f"{file}")

    except Exception as e:
        print(e) #             print("Arquivo não encontrado!")
    # finally:
    #     #For each  PDF on mainfolder, merge with those with PDF of the same name in EXAMES
    #     for file in os.listdir("ZIPS"):
    #         if file.endswith(".pdf"):
    #             for file2 in os.listdir("EXAMES"):
    #                 if file2.endswith(".pdf"):
    #                     MkPDF.MergePDF(f"{file}", f"{file2}")




# GENERATE A FUNCTION DO MERGE TWO PDFS
def MergePDF(file1, file2):
    pdf1 = open(file1, "rb")
    pdf2 = open(file2, "rb")
    pdf1_reader = PyPDF2.PdfFileReader(pdf1)
    pdf2_reader = PyPDF2.PdfFileReader(pdf2)
    pdf_writer = PyPDF2.PdfFileWriter()
    for page_num in range(pdf1_reader.numPages):
        page = pdf1_reader.getPage(page_num)
        pdf_writer.addPage(page)
    for page_num in range(pdf2_reader.numPages):
        page = pdf2_reader.getPage(page_num)
        pdf_writer.addPage(page)
    output = open(f"{file1}", "wb")
    pdf_writer.write(output)
    output.close()
    pdf1.close()
    pdf2.close()
    print("PDFs merged successfully!")



Change()
PDF_Process()
