import cv2
import pytesseract
import re
from typing import Dict, List, Tuple, Optional
import os
from utils.gpt_client import GPTClient


def extract_ultrasound_text(
    image_path: str,
    brightness_cut: int = 50,
    border_tol: float = 0.01,
    invert_thresh: int = 128,
) -> Tuple[List[str], List[Dict[str, float]]]:
    """🔍 extract_ultrasound_text
    Performs Optical Character Recognition (OCR) on an ultrasound image. The function trims dark borders, inverts colors if the background is black, and applies Tesseract to capture text. It then attempts to identify "label: value" pairs in each line and returns the text in lines and the structured data found.

    ### 🖥️ Parameters
    - `image_path` (`str`): Path to the image to be processed.
    - `brightness_cut` (`int`, optional): Brightness threshold to detect borders. Defaults to `50`.
    - `border_tol` (`float`, optional): Fraction of bright pixels that defines if a row/column is part of the image. Defaults to `0.01`.
    - `invert_thresh` (`int`, optional): Gray average below which the image is inverted before OCR. Defaults to `128`.

    ### 🔄 Returns
    - `Tuple[List[str], List[Dict[str, float]]]`: A list with each line of the extracted text and a list of dictionaries representing found measurements. Each dictionary contains the keys `identifier`, `value`, and `unit`.

    ### ⚠️ Raises
    - `FileNotFoundError`: If the image at `image_path` cannot be found.
    """
    # 1. leitura e conversão para tons de cinza
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise FileNotFoundError(f"Não achei {image_path}")
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 2. detecção de molduras escuras
    rows, cols = gray.shape
    bright = gray > brightness_cut
    col_keep = [bright[:, c].mean() > border_tol for c in range(cols)]
    row_keep = [bright[r, :].mean() > border_tol for r in range(rows)]
    try:
        x_min = col_keep.index(True)
        x_max = cols - col_keep[::-1].index(True)
        y_min = row_keep.index(True)
        y_max = rows - row_keep[::-1].index(True)
    except ValueError:
        x_min, x_max, y_min, y_max = 0, cols, 0, rows
    cropped = gray[y_min:y_max, x_min:x_max]

    # 3. inverter caso o fundo seja escuro
    if cropped.mean() < invert_thresh:
        cropped = cv2.bitwise_not(cropped)

    # 4. binarização
    _, bw = cv2.threshold(cropped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 5. OCR
    raw_text = pytesseract.image_to_string(bw, lang="eng+por")

    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]

    # 6. pares "rótulo-número" - padrão expandido
    measurements: List[Dict[str, float]] = []

    # Padrão principal para medidas biométricas
    measurement_pattern = re.compile(
        r"(?P<identifier>[A-Za-z0-9_ ]+)\s*[:=]?\s*(?P<value>[0-9]+(?:[.,][0-9]+)?)\s*(?P<unit>[\u00b5A-Za-z%/]+)?"
    )

    # Padrão para velocidades e fluxos (ecodoppler)
    velocity_pattern = re.compile(
        r"(?P<identifier>(?:PSV|EDV|RI|PI|S/D|TAV|VPS|VED|IP|IR|MV|AV|PV|TV))\s*[:=]?\s*(?P<value>[0-9]+(?:[.,][0-9]+)?)\s*(?P<unit>cm/s|m/s|mmHg|kPa)?"
    )

    # Padrão para percentis e z-scores
    percentile_pattern = re.compile(
        r"(?P<identifier>[A-Za-z0-9_ ]+)\s*(?:percentil|percentile|p)\s*(?P<value>[0-9]+(?:[.,][0-9]+)?)\s*(?P<unit>%|percentil)?"
    )

    for line in lines:
        # Tentar padrão de velocidade primeiro
        match = velocity_pattern.search(line)
        if match:
            identifier = match.group('identifier').strip()
            value = float(match.group('value').replace(',', '.'))
            unit = match.group('unit') or 'cm/s'  # default para velocidades
            measurements.append({
                'identifier': identifier,
                'value': value,
                'unit': unit,
            })
            continue

        # Tentar padrão de percentil
        match = percentile_pattern.search(line)
        if match:
            identifier = match.group('identifier').strip()
            value = float(match.group('value').replace(',', '.'))
            unit = match.group('unit') or '%'
            measurements.append({
                'identifier': identifier,
                'value': value,
                'unit': unit,
            })
            continue

        # Padrão principal
        match = measurement_pattern.search(line)
        if match:
            identifier = match.group('identifier').strip()
            value = float(match.group('value').replace(',', '.'))
            unit = match.group('unit') or ''
            measurements.append({
                'identifier': identifier,
                'value': value,
                'unit': unit,
            })

    if not measurements:
        raise ValueError('Nenhuma medida encontrada no texto extraído.')

    return lines, measurements


def identify_pathologies(text_lines: List[str]) -> List[Dict[str, str]]:
    """
    ### 🔍 identify_pathologies
    Identifies common pathologies in ultrasound and echocardiography reports using specific pattern matching. This function searches for pathological findings, abnormalities, and clinical conditions commonly found in medical imaging reports.

    ### 🖥️ Parameters
    - `text_lines` (`List[str]`): List of text lines extracted from OCR processing.

    ### 🔄 Returns
    - `List[Dict[str, str]]`: List of dictionaries containing identified pathologies. Each dictionary has keys 'pathology', 'severity', 'location', and 'description'.

    ### 💡 Example

    >>> identify_pathologies(['Esteatose hepática grau II', 'Hidronefrose bilateral leve'])
    [{'pathology': 'Esteatose hepática', 'severity': 'grau II', 'location': 'fígado', 'description': 'Esteatose hepática grau II'}]

    """
    pathologies = []

    # Padrões para patologias abdominais
    abdominal_patterns = {
        'esteatose': {
            'pattern': re.compile(r'esteatose\s+hep[aá]tica\s*(?:grau\s+)?([IVX]+|\d+|leve|moderada|grave|severa)?', re.IGNORECASE),
            'location': 'fígado',
            'description': 'Acúmulo de gordura no fígado'
        },
        'hidronefrose': {
            'pattern': re.compile(r'hidronefrose\s*(bilateral|unilateral|[\w\s]*)?(?:\s+(leve|moderada|grave|severa))?', re.IGNORECASE),
            'location': 'rim',
            'description': 'Dilatação do sistema coletor renal'
        },
        'hemangioma': {
            'pattern': re.compile(r'hemangioma\s*(?:hep[aá]tico)?\s*(?:de\s+)?([0-9,.\s]+(?:mm|cm))?', re.IGNORECASE),
            'location': 'fígado',
            'description': 'Tumor benigno vascular'
        },
        'cisto': {
            'pattern': re.compile(r'cisto\s*(?:simples|complexo|septado)?\s*(?:de\s+)?([0-9,.\s]+(?:mm|cm))?', re.IGNORECASE),
            'location': 'variável',
            'description': 'Lesão cística'
        },
        'litíase': {
            'pattern': re.compile(r'lit[ií]ase\s*(?:biliar|renal|vesicular)?\s*(?:de\s+)?([0-9,.\s]+(?:mm|cm))?', re.IGNORECASE),
            'location': 'variável',
            'description': 'Presença de cálculos'
        },
        'espessamento': {
            'pattern': re.compile(r'espessamento\s+(?:parietal|da\s+parede)\s*(?:de\s+)?([0-9,.\s]+(?:mm|cm))?', re.IGNORECASE),
            'location': 'variável',
            'description': 'Espessamento de parede'
        }
    }

    # Padrões para patologias cardíacas/vasculares
    cardiac_patterns = {
        'estenose': {
            'pattern': re.compile(r'estenose\s+(?:a[oó]rtica|mitral|tricúspide|pulmonar)\s*(?:leve|moderada|grave|severa)?', re.IGNORECASE),
            'location': 'coração',
            'description': 'Estreitamento valvar'
        },
        'insuficiência': {
            'pattern': re.compile(r'insufici[eê]ncia\s+(?:a[oó]rtica|mitral|tricúspide|pulmonar)\s*(?:leve|moderada|grave|severa)?', re.IGNORECASE),
            'location': 'coração',
            'description': 'Regurgitação valvar'
        },
        'hipertrofia': {
            'pattern': re.compile(r'hipertrofia\s+(?:ventricular|septal|concêntrica|excêntrica)\s*(?:leve|moderada|grave|severa)?', re.IGNORECASE),
            'location': 'coração',
            'description': 'Aumento da espessura miocárdica'
        },
        'dilatação': {
            'pattern': re.compile(r'dilata[çc][aã]o\s+(?:ventricular|atrial|a[oó]rtica)\s*(?:leve|moderada|grave|severa)?', re.IGNORECASE),
            'location': 'coração',
            'description': 'Aumento das dimensões cardíacas'
        },
        'derrame': {
            'pattern': re.compile(r'derrame\s+peric[aá]rdico\s*(?:leve|moderado|grave|severo)?', re.IGNORECASE),
            'location': 'pericárdio',
            'description': 'Acúmulo de líquido no pericárdio'
        }
    }

    # Padrões para patologias vasculares
    vascular_patterns = {
        'placa': {
            'pattern': re.compile(r'placa\s+(?:ateroscler[oó]tica|calc[ií]fica|mista)\s*(?:com\s+)?(?:estenose\s+)?([0-9]+%)?', re.IGNORECASE),
            'location': 'vaso',
            'description': 'Placa aterosclerótica'
        },
        'trombo': {
            'pattern': re.compile(r'trombo\s*(?:mural|intraluminal|oclusivo)?', re.IGNORECASE),
            'location': 'vaso',
            'description': 'Coágulo intravascular'
        },
        'aneurisma': {
            'pattern': re.compile(r'aneurisma\s*(?:de\s+)?([0-9,.\s]+(?:mm|cm))?', re.IGNORECASE),
            'location': 'vaso',
            'description': 'Dilatação anormal do vaso'
        }
    }

    # Padrões para patologias obstétricas
    obstetric_patterns = {
        'oligoâmnio': {
            'pattern': re.compile(r'oligo[aâ]mnio|oligohidr[aâ]mnio', re.IGNORECASE),
            'location': 'útero',
            'description': 'Diminuição do líquido amniótico'
        },
        'polidrâmnio': {
            'pattern': re.compile(r'polidr[aâ]mnio|polihidr[aâ]mnio', re.IGNORECASE),
            'location': 'útero',
            'description': 'Aumento do líquido amniótico'
        },
        'restrição': {
            'pattern': re.compile(r'restri[çc][aã]o\s+(?:de\s+)?crescimento\s+(?:fetal|intrauterino)', re.IGNORECASE),
            'location': 'feto',
            'description': 'Restrição do crescimento fetal'
        },
        'malformação': {
            'pattern': re.compile(r'malforma[çc][aã]o\s+(?:fetal|cong[eê]nita)', re.IGNORECASE),
            'location': 'feto',
            'description': 'Malformação congênita'
        }
    }

    # Combinar todos os padrões
    all_patterns = {**abdominal_patterns, **cardiac_patterns, **vascular_patterns, **obstetric_patterns}

    # Buscar patologias nas linhas de texto
    for line in text_lines:
        for pathology_name, pattern_info in all_patterns.items():
            match = pattern_info['pattern'].search(line)
            if match:
                severity = ''
                if match.groups():
                    severity = match.group(1) if match.group(1) else ''

                pathologies.append({
                    'pathology': pathology_name.replace('_', ' ').title(),
                    'severity': severity.strip(),
                    'location': pattern_info['location'],
                    'description': pattern_info['description'],
                    'full_text': line.strip()
                })

    return pathologies


def extract_doppler_parameters(text_lines: List[str]) -> List[Dict[str, any]]:
    """
    ### 🩺 extract_doppler_parameters
    Extracts Doppler ultrasound parameters including velocities, resistance indices, and flow patterns. This function is specialized for cardiovascular and vascular ultrasound analysis.

    ### 🖥️ Parameters
    - `text_lines` (`List[str]`): List of text lines extracted from OCR processing.

    ### 🔄 Returns
    - `List[Dict[str, any]]`: List of dictionaries containing Doppler parameters. Each dictionary includes parameter name, value, unit, and reference ranges.

    ### 💡 Example

    >>> extract_doppler_parameters(['PSV: 120 cm/s', 'EDV: 30 cm/s', 'RI: 0.75'])
    [{'parameter': 'PSV', 'value': 120.0, 'unit': 'cm/s', 'reference_range': '50-150 cm/s'}]

    """
    doppler_params = []

    # Padrões específicos para parâmetros Doppler
    doppler_patterns = {
        'PSV': {
            'pattern': re.compile(r'PSV\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)\s*(cm/s|m/s)?', re.IGNORECASE),
            'full_name': 'Peak Systolic Velocity',
            'reference_range': '50-150 cm/s (varia por vaso)',
            'unit': 'cm/s'
        },
        'EDV': {
            'pattern': re.compile(r'EDV\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)\s*(cm/s|m/s)?', re.IGNORECASE),
            'full_name': 'End Diastolic Velocity',
            'reference_range': '15-40 cm/s (varia por vaso)',
            'unit': 'cm/s'
        },
        'RI': {
            'pattern': re.compile(r'RI\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)', re.IGNORECASE),
            'full_name': 'Resistance Index',
            'reference_range': '0.5-0.8 (varia por órgão)',
            'unit': 'adimensional'
        },
        'PI': {
            'pattern': re.compile(r'PI\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)', re.IGNORECASE),
            'full_name': 'Pulsatility Index',
            'reference_range': '0.8-1.2 (varia por vaso)',
            'unit': 'adimensional'
        },
        'S/D': {
            'pattern': re.compile(r'S/D\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)', re.IGNORECASE),
            'full_name': 'Systolic/Diastolic Ratio',
            'reference_range': '2.0-4.0 (varia por vaso)',
            'unit': 'adimensional'
        },
        'TAV': {
            'pattern': re.compile(r'TAV\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)\s*(cm/s|m/s)?', re.IGNORECASE),
            'full_name': 'Time Averaged Velocity',
            'reference_range': '20-80 cm/s (varia por vaso)',
            'unit': 'cm/s'
        }
    }

    # Buscar parâmetros nas linhas de texto
    for line in text_lines:
        for param_name, param_info in doppler_patterns.items():
            match = param_info['pattern'].search(line)
            if match:
                value = float(match.group(1).replace(',', '.'))
                unit = match.group(2) if len(match.groups()) > 1 and match.group(2) else param_info['unit']

                doppler_params.append({
                    'parameter': param_name,
                    'full_name': param_info['full_name'],
                    'value': value,
                    'unit': unit,
                    'reference_range': param_info['reference_range'],
                    'source_line': line.strip()
                })

    return doppler_params


def enhanced_text_extraction(name: str) -> Dict[str, any]:
    """
    ### 🔍 enhanced_text_extraction
    Enhanced text extraction function that combines OCR, pathology identification, and Doppler parameter extraction. This function provides comprehensive analysis of ultrasound images with medical context.

    ### 🖥️ Parameters
    - `name` (`str`): Patient name for folder structure and file naming.

    ### 🔄 Returns
    - `Dict[str, any]`: Dictionary containing all extracted information including OCR text, measurements, pathologies, and Doppler parameters.

    ### ⚠️ Raises
    - `FileNotFoundError`: If the patient directory or images are not found.
    - `OSError`: If there are issues with file operations.

    ### 💡 Example

    >>> enhanced_text_extraction("João Silva")
    {'ocr_findings': [...], 'measurements': [...], 'pathologies': [...], 'doppler_params': [...]}

    """
    reports_dir = os.path.join("Pacientes", name, "Report")
    images_dir = os.path.join("Pacientes", name, "Images")

    if not os.path.exists(images_dir):
        raise FileNotFoundError(f"Diretório de imagens não encontrado: {images_dir}")

    gpt = GPTClient()

    # Estrutura para armazenar todos os dados extraídos
    extraction_results = {
        'ocr_findings': [],
        'measurements': [],
        'pathologies': [],
        'doppler_params': [],
        'enhanced_lines': []
    }

    # Processar cada imagem
    for img in os.listdir(images_dir):
        if img.lower().endswith((".jpeg", ".jpg", ".png", ".bmp")):
            img_path = os.path.join(images_dir, img)

            try:
                # Extrair texto e medidas
                text_lines, measurements = extract_ultrasound_text(img_path)

                # Identificar patologias
                pathologies = identify_pathologies(text_lines)

                # Extrair parâmetros Doppler
                doppler_params = extract_doppler_parameters(text_lines)

                # Melhorar texto com GPT
                enhanced_lines = []
                for line in text_lines:
                    if line.strip():
                        enhanced_line = gpt.enhance_text(line)
                        enhanced_lines.append(enhanced_line)
                    else:
                        enhanced_lines.append("")

                # Adicionar aos resultados
                extraction_results['ocr_findings'].extend(text_lines)
                extraction_results['measurements'].extend(measurements)
                extraction_results['pathologies'].extend(pathologies)
                extraction_results['doppler_params'].extend(doppler_params)
                extraction_results['enhanced_lines'].extend(enhanced_lines)

            except Exception as e:
                print(f"Erro ao processar {img}: {e}")
                continue

    # Salvar resultados detalhados
    detailed_report_path = os.path.join(reports_dir, f"{name}_detailed_analysis.txt")
    with open(detailed_report_path, "w", encoding="utf-8") as report_file:
        report_file.write("=== ANÁLISE DETALHADA DE ULTRASSOM ===\n\n")

        # Seção de medidas
        if extraction_results['measurements']:
            report_file.write("MEDIDAS BIOMÉTRICAS:\n")
            for measurement in extraction_results['measurements']:
                report_file.write(f"- {measurement['identifier']}: {measurement['value']} {measurement['unit']}\n")
            report_file.write("\n")

        # Seção de patologias
        if extraction_results['pathologies']:
            report_file.write("PATOLOGIAS IDENTIFICADAS:\n")
            for pathology in extraction_results['pathologies']:
                report_file.write(f"- {pathology['pathology']}")
                if pathology['severity']:
                    report_file.write(f" ({pathology['severity']})")
                report_file.write(f" - {pathology['description']}\n")
                report_file.write(f"  Localização: {pathology['location']}\n")
                report_file.write(f"  Texto original: {pathology['full_text']}\n\n")

        # Seção de parâmetros Doppler
        if extraction_results['doppler_params']:
            report_file.write("PARÂMETROS DOPPLER:\n")
            for param in extraction_results['doppler_params']:
                report_file.write(f"- {param['full_name']} ({param['parameter']}): {param['value']} {param['unit']}\n")
                report_file.write(f"  Referência: {param['reference_range']}\n")

        # Texto melhorado
        report_file.write("\nTEXTO MELHORADO (GPT):\n")
        for line in extraction_results['enhanced_lines']:
            if line.strip():
                report_file.write(f"- {line}\n")

    return extraction_results


def text_extraction(name):
    """
    ### 📝 text_extraction
    Legacy function maintained for backward compatibility. Processes OCR text extraction and generates basic reports. For enhanced functionality, use enhanced_text_extraction instead.

    ### 🖥️ Parameters
    - `name` (`str`): Patient name for folder structure and file naming.

    ### 🔄 Returns
    - `List[str]`: List of enhanced OCR findings for compatibility with existing code.

    ### 💡 Example

    >>> text_extraction("João Silva")
    ['Enhanced OCR line 1', 'Enhanced OCR line 2', ...]

    """
    reports_dir = os.path.join("Pacientes", name, "Report")
    images_dir = os.path.join("Pacientes", name, "Images")
    gpt = GPTClient()
    all_ocr_findings = []

    os.makedirs(reports_dir, exist_ok=True)

    txt_path = os.path.join(reports_dir, f"{name}_report.txt")

    with open(txt_path, "w", encoding="utf-8") as txt_file:
        for img in os.listdir(images_dir):
            if img.lower().endswith((".jpeg", ".jpg", ".png", ".bmp")):
                img_path = os.path.join(images_dir, img)
                text, _ = extract_ultrasound_text(img_path)
                enhanced_lines = []
                for line in text:
                    if line.strip():
                        enhanced_line = gpt.enhance_text(line)
                        enhanced_lines.append(enhanced_line)
                        all_ocr_findings.append(enhanced_line)
                    else:
                        enhanced_lines.append("")
                txt_file.write(f"# {img}\n" + "\n".join(enhanced_lines) + "\n")

    return all_ocr_findings