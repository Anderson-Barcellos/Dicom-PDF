from PIL import Image
import os
from fpdf import FPDF
import numpy as np
import matplotlib.pyplot as plt


# Configurações da página A4
def Make_PDF():
    A4_WIDTH_MM = 210
    A4_HEIGHT_MM = 297
    MM_TO_PX = 96 / 25.4  # 96 pixels por polegada / 25.4 mm por polegada

    # Configurações das imagens na tabela 2x4
    IMAGES_PER_ROW = 2
    ROWS = 4
    SPACING_MM = 5  # Espaço horizontal entre as imagens em mm
    SPACING_VERTICAL_MM = 7  # Espaço vertical entre as imagens em mm

    # Calcula o tamanho disponível para cada imagem, considerando o espaço entre elas
    available_width = A4_WIDTH_MM - ((IMAGES_PER_ROW + 1) * SPACING_MM)
    available_height = A4_HEIGHT_MM - ((ROWS + 1) * SPACING_VERTICAL_MM)
    image_width_mm = available_width / IMAGES_PER_ROW
    image_height_mm = available_height / ROWS

    # Cria um PDF A4
    pdf = FPDF(orientation="P", unit="mm", format="A4")

    # Encontra todas as imagens JPG no diretório atual
    images = [
        f
        for f in os.listdir(".")
        if f.lower().endswith((".jpg", ".jpeg", ".JPG", ".JPEG"))
    ]

    # Divide as imagens em grupos de 8
    chunks = [images[i: i + 8] for i in range(0, len(images), 8)]

    for chunk in chunks:
        pdf.add_page()

        if len(chunk) <= 6:
            ROWS = 3
            SPACING_VERTICAL_MM = 18
        else:
            ROWS = 4
            SPACING_VERTICAL_MM = 7

        # Adiciona as imagens ao PDF, mantendo a proporção
        for i, image_path in enumerate(chunk):
            img = Image.open(image_path)
            img_width_mm, img_height_mm = img.size[0] / \
                MM_TO_PX, img.size[1] / MM_TO_PX

            # Mantém a proporção da imagem
            scale_factor = min(
                image_width_mm / img_width_mm, image_height_mm / img_height_mm
            )
            new_width_mm = img_width_mm * scale_factor
            new_height_mm = img_height_mm * scale_factor

            # Calcula a posição centralizada da imagem
            x = (
                SPACING_MM
                + (i % IMAGES_PER_ROW) * (image_width_mm + SPACING_MM)
                + (image_width_mm - new_width_mm) / 2
            )
            y = (
                SPACING_VERTICAL_MM
                + (i // IMAGES_PER_ROW) *
                (image_height_mm + SPACING_VERTICAL_MM)
                + (image_height_mm - new_height_mm) / 4
            )

            # Adiciona a imagem ao PDF sem redimensionar o arquivo de imagem original
            pdf.image(image_path, x=x, y=y, w=new_width_mm, h=new_height_mm)

    # Salva o PDF
    pdf.output("imagens_organizadas.pdf")


if __name__ == "__main__":
    Make_PDF()


def create_percentile_plot(plots_data, output_plot):
    weeks = np.arange(20, 40, 2)  # Semanas de gestação
    percentil_3 = np.array(
        [150, 250, 400, 650, 950, 1350, 1800, 2300, 2700, 3100])
    percentil_50 = np.array(
        [200, 350, 550, 900, 1300, 1750, 2300, 2800, 3300, 3800])
    percentil_97 = np.array(
        [250, 450, 700, 1150, 1600, 2200, 2700, 3200, 3700, 4200])

    plt.figure(figsize=(10, 6))

    for plot_name, plot_values in plots_data.items():
        x_vals, y_vals = zip(*plot_values)
        plt.plot(weeks[: len(x_vals)], y_vals, "ko-", label=plot_name)

    plt.plot(weeks, percentil_3, "b--", label="3% Percentile")
    plt.plot(weeks, percentil_50, "g-", label="50% Percentile")
    plt.plot(weeks, percentil_97, "r--", label="97% Percentile")
    plt.fill_between(
        weeks,
        percentil_3,
        percentil_97,
        color="lightgrey",
        alpha=0.5,
        label="3%-97% Range",
    )

    plt.xlabel("Weeks of Gestation")
    plt.ylabel("Estimated Fetal Weight (g)")
    plt.title("Fetal Growth Chart with Percentiles")
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.xlim(20, 40)
    plt.ylim(0, 4500)
    plt.tight_layout()

    plt.savefig(output_plot)
    plt.close()
