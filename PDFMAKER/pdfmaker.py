import os
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Image as rlImage
from reportlab.lib import colors


def MkPDF(name: str):
    """
    📄 MkPDF
    Generates a PDF document from a set of image files located in a specific patient directory. The images are arranged in a grid layout per page, with their display size automatically adjusted to fit the A4 page while maintaining aspect ratio. This function is typically used in a medical imaging workflow to compile patient images into a single PDF report.

    ### 🖥️ Parameters
        - `name` (`str`): The base name of the patient folder and PDF file. This should correspond to the patient identifier or folder name containing the images and where the PDF will be saved.

    ### 🔄 Returns
        - `None`: The function creates and saves a PDF file to disk; it does not return any value.

    ### ⚠️ Raises
        - `FileNotFoundError`: If the expected image directory does not exist.
        - `OSError`: If there is an error reading image files or writing the PDF.

    ### 💡 Example

    >>> MkPDF("20240601_Anders")
    # Creates 'Patients/Anders/Report/Anders.pdf' with all images from 'Patients/Anders/Images'
    """

    # Margens do documento
    doc_margin = 20

    # Inicializar o PDF
    pdf = SimpleDocTemplate(
        os.path.join("Patients", name, "Report", f"{name}.pdf"),
        pagesize=A4,
        rightMargin=doc_margin,
        leftMargin=doc_margin,
        topMargin=20,
        bottomMargin=doc_margin,
    )

    # Criar a pasta de imagens
    folder = os.path.join("Patients", name, "Images")

    # Table settings
    num_rows = 4
    num_cols = 2
    cell_padding = 5

    width, height = A4
    width -= 1 * doc_margin  # Adjust width for margins
    height -= 1 * doc_margin  # Adjust height for margins
    table_width = 0.98 * width
    table_height = 0.98 * height
    cell_width = table_width / num_cols
    cell_height = table_height / num_rows

    # List all JPG images in the folder

    def Wrap_PDF():
        """Wrapper para a função de criação do PDF"""
        images = [
            f
            for f in os.listdir(folder)
            if f.endswith(".jpeg")
            or f.endswith(".jpg")
            or f.endswith(".png")
            or f.endswith(".JPG")
            or f.endswith(".bmp")
        ]
        data = []
        data2 = []
        # Start table data list

        def imager(data: list, images: list) -> list:
            """Função para adicionar imagens à lista de caminhos de dados
            #### Parâmetros:
            - data: list
                Lista de caminhos de dados da tabela.
            - images: list
                Lista de caminhos de imagens.
            """
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

        # Create the PDF file accordingly to the number of images
        if len(images) <= 8:
            data = imager(data, images)
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
            print("PDF criado com sucesso")

        else:
            half = images[:8]
            data = imager(data, half)
            other_half = images[8:]
            data2 = imager(data2, other_half)

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
            pdf.build([table, table2])
            print("PDF criado com sucesso")

    Wrap_PDF()
