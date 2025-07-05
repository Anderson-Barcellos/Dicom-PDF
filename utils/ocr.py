import cv2  # type: ignore
import pytesseract  # type: ignore
import re
from typing import Dict, List, Tuple, Union


def extract_ultrasound_text(
    image_path: str,
    brightness_cut: int = 50,
    border_tol: float = 0.01,
    invert_thresh: int = 128,
) -> Tuple[str, List[Dict[str, Union[str, float]]]]:
    """Realiza OCR em imagem de ultrassom.

    A função corta bordas escuras, inverte as cores caso o fundo seja preto e
    aplica o Tesseract para capturar o texto. Ao final, tenta identificar pares
    ``rotulo: valor`` em cada linha e retorna o texto em linhas e os dados
    estruturados encontrados.

    Parameters
    ----------
    image_path : str
        Caminho da imagem a ser processada.
    brightness_cut : int, optional
        Limite de brilho para detectar as bordas. Padrão ``50``.
    border_tol : float, optional
        Fração de pixels claros que define se a linha/coluna faz parte da imagem.
        Padrão ``0.01``.
    invert_thresh : int, optional
        Média de cinza abaixo da qual a imagem é invertida antes do OCR. Padrão
        ``128``.

    Returns
    -------
    Tuple[str, List[Dict[str, Union[str, float]]]
        Uma string com o texto extraído e uma lista de dicionários
        representando medidas encontradas. Cada dicionário possui as chaves
        ``identifier``, ``value`` e ``unit``.
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

    # 6. pares "rótulo-número"
    measurements: List[Dict[str, Union[str, float]]] = []
    pattern = re.compile(
        r"(?P<identifier>[A-Za-z0-9_ ]+)\s*[:=]?\s*(?P<value>[0-9]+(?:[.,][0-9]+)?)\s*(?P<unit>[\u00b5A-Za-z%/]+)?"
    )

    for line in lines:
        match = pattern.search(line)
        if match:
            identifier = match.group('identifier').strip()
            value = float(match.group('value').replace(',', '.'))
            unit = match.group('unit') or ''
            measurements.append({
                'identifier': identifier,
                'value': value,
                'unit': unit,
            })

    # Join extracted lines into a single text blob because downstream code
    # expects a string and calls `.splitlines()` on it.
    text_out = "\n".join(lines)

    # Even if no measurements are detected we still return the raw OCR text so
    # that downstream processing (e.g. PDF generation) can continue without
    # raising an exception.  An empty measurements list signals that nothing
    # was found instead of crashing the pipeline.
    return text_out, measurements
