from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.pagesizes import letter, A4
from typing import List, Dict, Tuple
from SR2PLOT import create_other_plots
import pydicom
from typing import Any
import os


def extract_biometrical_data(data):
    extracted_data = {}
    keys_to_extract = [
        "Composite Ultrasound Age",
        "Estimated Weight",
        "Abdominal Circumference",
        "Biparietal Diameter",
        "Femur Length",
        "Head Circumference",
        "Fetal Heart Rate",
        "PatientName",
    ]

    def recursive_extract(d):
        for key, value in d.items():
            if key in keys_to_extract and isinstance(value, (int, float)):
                extracted_data[key] = value
            elif isinstance(value, dict):
                recursive_extract(value)
            elif (
                isinstance(value, tuple)
                and len(value) == 2
                and isinstance(value[1], dict)
            ):
                recursive_extract(value[1])

    recursive_extract(data)
    return extracted_data


def ExtractSR(sequence, level=4) -> Tuple[List, Dict]:
    """Function to extract measurements from DICOM SR content sequence.
    ### Parameters

    - sequence (Sequence):
        The sequence to extract measurements from a `dicomread(instance).ContentSequence` attribute.

    - level (int):
        The level of the nested content.
    """

    measurements = []
    biometrical_data = {}

    for item in sequence:

        if not hasattr(item, "ValueType") or not item.ValueType:
            continue

        if item.ValueType == "NUM":

            concept_name = item.ConceptNameCodeSequence[0].CodeMeaning
            numeric_value = float(item.MeasuredValueSequence[0].NumericValue)
            unit_code = (
                item.MeasuredValueSequence[0]
                .MeasurementUnitsCodeSequence[0]
                .CodeMeaning
            )

            measurements.append((f"{concept_name}: {numeric_value}{unit_code}", level))
            biometrical_data[concept_name] = numeric_value
        elif item.ValueType == "CONTAINER" and hasattr(item, "ContentSequence"):

            nested_measurements, nested_biometrical_data = ExtractSR(
                item.ContentSequence, level + 1
            )
            measurements.extend(nested_measurements)
            biometrical_data.update(nested_biometrical_data)

    return measurements, biometrical_data


def plot_biometrical_data(biometrical_data):
    weeks = biometrical_data.get("Composite Ultrasound Age", 0) // 7
    print(f"Weeks: {weeks}")
    print(f"Biometrical data: {biometrical_data}")

    mapping = {
        "Head Circumference": "Circunferência Craniana (HC)",
        "Biparietal Diameter": "Diâmetro Biparietal (BPD)",
        "Abdominal Circumference": "Circunferência Abdominal (AC)",
        "Femur Length": "Comprimento do Fêmur (FL)",
        "Estimated Weight": "Peso Fetal Estimado (EFW)",
    }

    for biometry, value in biometrical_data.items():
        if (
            biometry in mapping
            and biometry != "Estimated Weight"
            and biometry != "Composite Ultrasound Age"
        ):
            create_other_plots(mapping[biometry], 10 * value, weeks)
        elif biometry == "Estimated Weight" and biometry != "Composite Ultrasound Age":
            create_other_plots("Peso Fetal Estimado (EFW)", value, weeks)


from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT


def pdf_report(name, measurements, biometrical_data):
    """Gera o relatório em PDF a partir dos dados biométricos coletados.

    Parameters
    ----------
    name : str
        Nome base do relatório gerado.
    measurements : list
        Lista de medições extraídas do DICOM.
    biometrical_data : dict
        Valores numéricos que alimentam os gráficos de crescimento fetal.

    Returns
    -------
    None
        O PDF é salvo em ``{name}_report.pdf`` e, em seguida, o texto é extraído
        via OCR para criar ``{name}_report.txt``.
    """
    story = []
    doc = SimpleDocTemplate(
        f"{name}_report.pdf",
        pagesize=A4,
        topMargin=7 * mm,
        bottomMargin=7 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    # Define page width and height
    page_width, page_height = A4

    styles = getSampleStyleSheet()
    # Create a custom style for smaller text
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["Normal"],
            fontSize=9,
            leading=11,
            alignment=TA_LEFT,
        )
    )

    title = Paragraph("DICOM SR Measurement Report", styles["Title"])
    story.append(title)
    story.append(Spacer(1, 6 * mm))

    # Add measurements
    for biometry, value in biometrical_data.items():
        if biometry in [
            "Abdominal Circumference",
            "Femur Length",
            "Head Circumference",
            "Biparietal Diameter",
        ]:
            text = f"{biometry}: {10*value:.2f} mm"
        elif biometry == "Estimated Weight":
            text = f"{biometry}: {value:.0f} g"
        else:
            text = f"{biometry}: {value}"
        p = Paragraph(text, styles["Small"])
        story.append(p)

    story.append(PageBreak())

    # Add plots to the PDF
    plot_files = [
        "Circunferência Craniana (HC).png",
        "Diâmetro Biparietal (BPD).png",
        "Circunferência Abdominal (AC).png",
        "Comprimento do Fêmur (FL).png",
        "Peso Fetal Estimado (EFW).png",
    ]

    # Calculate image dimensions
    image_width = page_width - 20
    image_height = image_width * 0.65

    # two rows per page with an image inside
    for i in range(1, len(plot_files), 2):
        if i + 1 >= len(plot_files):
            break
        img1 = Image(plot_files[i], width=image_width, height=image_height)
        img2 = Image(plot_files[i + 1], width=image_width, height=image_height)
        story.append(img1)
        # space
        story.append(Spacer(1, 6 * mm)) if i + 1 < len(plot_files) else None
        story.append(img2)
        story.append(PageBreak())

    doc.build(story)

    print(
        f"Total of {len(measurements)} measurements were found and reported in {name}_report.pdf."
    )


def save_to_txt_report(name, measurements) -> None:
    """Salva as medições em um arquivo ``.txt`` gerado por OCR.

    Parameters
    ----------
    name : str
        Nome base do relatório.
    measurements : list
        Lista de tuplas contendo a descrição, o valor e a unidade de cada
        medição.

    Returns
    -------
    None
        Gera ``{name}_report.txt`` com o conteúdo extraído do PDF por OCR.
    """
    with open(f"{name}_report.txt", "w") as f:
        f.write("Relatório de Medições DICOM SR\n")
        f.write("=" * 30 + "\n\n")

        for concept_name, numeric_value, unit_code, level in measurements:
            indent = " " * (
                level * 4
            )  # Indenta com base no nível (usa 4 espaços por nível)
            text = f"{concept_name}: {numeric_value} {unit_code}\n"
            f.write(text)

    print(f"Total de {len(measurements)} medidas foram salvas em report.txt.")


if __name__ == "__main__":
    print(pydicom.dcmread("SR.dcm").get_item((0x0040, 0xA121)))
    ds = pydicom.dcmread("SR.dcm").ContentSequence
    measurements, biometrical_data = ExtractSR(ds)
    print(measurements)
    biometrical_data = extract_biometrical_data(biometrical_data)

    plot_biometrical_data(biometrical_data)
    pdf_report("report", measurements, biometrical_data)
