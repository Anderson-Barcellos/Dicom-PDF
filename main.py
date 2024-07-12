from DicomManager.unzip import Unzipper
from DicomManager.DICOM import DICOM2JPEG

import os
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Image as rlImage
from reportlab.lib import colors



def MkPDF(name: str):
    """Function to create a PDF file with images. The images will be added to the PDF without resizing, but their display size will be adjusted to fit the page."""
    # Initialize PDF
    # Margens do documento
    doc_margin = 20

    # Initialize PDF with adjusted margins
    pdf = SimpleDocTemplate(f"{name[15:]}.pdf", pagesize=A4, rightMargin=doc_margin, leftMargin=doc_margin, topMargin=20, bottomMargin=doc_margin)
    



    # Create current folder path
    folder = os.path.join(os.getcwd(), "Images")

    # Table settings
    num_rows = 4
    num_cols = 2
    cell_padding = 5


    width, height = A4
    width -= 1 * doc_margin  # Adjust width for margins
    height -= 1 * doc_margin  # Adjust height for margins
    table_width = 0.98* width
    table_height = 0.98 * height
    cell_width = table_width / num_cols
    cell_height = table_height / num_rows

    # List all JPG images in the folder

    def T(): 
        images = [
            f for f in os.listdir(folder) if f.endswith(".jpeg") or f.endswith(".jpg") or f.endswith(".png") or f.endswith(".JPG")
        ]
        data = []
        data2 = []
        # Start table data list
        
        def imager(data,images): 
            # Add images to the data list
            for i in range(num_rows):
                row = []
                for j in range(num_cols):
                    try:
                        img_path = images.pop(0)
                        img_path = os.path.join(folder, img_path)
                    except IndexError:
                        row.append("")  # No more images to add
                        continue

            
                    img = Image.open(img_path)
                    rl_img = rlImage(img_path)


                    # Adjust the display size of the image in the PDF
                    w_ratio = (cell_width - 2 * cell_padding) / img.size[0]
                    h_ratio = (cell_height - 2 * cell_padding) / img.size[1]
                    ratio = min(w_ratio, h_ratio)

                    rl_img.drawHeight = img.size[1] * ratio
                    rl_img.drawWidth = img.size[0] * ratio

                    row.append(rl_img)

                data.append(row)
            return data
               # Create the table

        if len(images) <=8:
            data = imager(data,images)
            table = Table(data)
            table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0, colors.transparent),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )
            )
            pdf.build([table])
            print(f"PDF criado com sucesso")

                  
        else:
            half =images[:8]
            data = imager(data,half)
            other_half = images[8:]
            data2 = imager(data2,other_half)

            table = Table(data)
            table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0, colors.transparent),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )
            )

            table2 = Table(data2)
            table2.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0, colors.transparent),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )
            )
            pdf.build([table,table2])
            print(f"PDF criado com sucesso")
    T()




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



# ORTHANC
from pyorthanc import Orthanc
import time
import json

orthanc = Orthanc("http://usview.tech:8042", "orthanc", "orthanc")

while True:
    # Load pacientes atualizados
    patients = None
    with open('patients.json') as json_file:
        patients = json.load(json_file)

    # Atualização os pacientes
    latest_patients = orthanc.get_patients()
    if patients == latest_patients:
        print("Nenhum novo paciente encontrado")
        time.sleep(60)
    else:
        new_patients = [p for p in latest_patients if p not in patients]

        # Processo para cada novo paciente
        for patient in new_patients:
            response = orthanc.get_patients_id_archive(str(patient))
            with open(f"ZIPS/{patient}.zip", "wb") as f:
                f.write(response)
            Extract_Convert_Img(f"{patient}.zip")

        # Atualizar pacientes
        patients = latest_patients


        
        with open('patients.json', 'w') as json_file:
            json.dump(patients, json_file)

        # Esperar um momento (tempo em segundos) antes de verificar novamente
        time.sleep(60)