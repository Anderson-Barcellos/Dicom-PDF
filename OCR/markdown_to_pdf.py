from pathlib import Path
from pyorthanc.retrieve import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
import markdown2

def markdown_to_pdf(markdown_file: Path, pdf_file: Path):
    """
    Converte um arquivo markdown em PDF formatado
    """
    # Ler o conteúdo markdown
    with open(markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Converter markdown para HTML
    html_content = markdown2.markdown(md_content)

    # Criar o PDF
    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Justified',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=14,
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=20
    ))

    # Processar o conteúdo
    story = []
    lines = md_content.split('\n')

    for line in lines:
        line = line.strip()

        if line.startswith('# '):
            # Título principal
            story.append(Paragraph(line[2:], styles['CustomTitle']))
            story.append(Spacer(1, 12))
        elif line.startswith('## '):
            # Subtítulo
            story.append(Paragraph(line[3:], styles['Heading2']))
            story.append(Spacer(1, 6))
        elif line.startswith('### '):
            # Sub-subtítulo
            story.append(Paragraph(line[4:], styles['Heading3']))
            story.append(Spacer(1, 6))
        elif line.startswith('**') and line.endswith('**'):
            # Texto em negrito
            story.append(Paragraph(f"<b>{line[2:-2]}</b>", styles['Normal']))
            story.append(Spacer(1, 6))
        elif line:
            # Texto normal
            # Converter markdown inline para tags HTML
            line = line.replace('**', '<b>', 1).replace('**', '</b>', 1)
            line = line.replace('*', '<i>', 1).replace('*', '</i>', 1)
            story.append(Paragraph(line, styles['Justified']))
            story.append(Spacer(1, 6))

    # Gerar o PDF
    doc.build(story)
    print(f"PDF do laudo gerado: {pdf_file}")
    os.remove(markdown_file)