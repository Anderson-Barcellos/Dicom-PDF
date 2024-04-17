import os
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Image as rlImage
from reportlab.lib import colors
from io import BytesIO


def MkPDF(name: str):
    """Function to create a PDF file with images. The images will be added to the PDF without resizing, but their display size will be adjusted to fit the page."""
    # Initialize PDF
    pdf = SimpleDocTemplate(f"{name[15:]}.pdf", pagesize=A4)

    # Create current folder path
    folder = os.path.join(os.getcwd(), "Images")

    # Table settings
    num_rows = 4
    num_cols = 2
    cell_padding = 5

    # Page and table dimensions
    width, height = A4
    table_width = 0.95 * width
    table_height = 0.95 * height
    cell_width = table_width / num_cols
    cell_height = table_height / num_rows

    # List all JPG images in the folder
    images = [
        f for f in os.listdir(folder) if f.endswith(".jpeg") or f.endswith(".jpg") or f.endswith(".png") or f.endswith(".JPG")
    ]

    # Start table data list
    data = []

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

            # Convert PIL image to a ReportLab Image
            img_byte_arr = BytesIO()
            img = Image.open(img_path)
            img.save(img_byte_arr, format="JPEG")
            img_byte_arr = img_byte_arr.getvalue()
            rl_img = rlImage(BytesIO(img_byte_arr))

            # Adjust the display size of the image in the PDF
            w_ratio = (cell_width - 2 * cell_padding) / img.size[0]
            h_ratio = (cell_height - 2 * cell_padding) / img.size[1]
            ratio = min(w_ratio, h_ratio)

            rl_img.drawHeight = img.size[1] * ratio
            rl_img.drawWidth = img.size[0] * ratio

            row.append(rl_img)

        data.append(row)

    # Create the table
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

    print("Done!")

