import cv2
import pytesseract
import re
from typing import Tuple, Dict


def extract_ultrasound_text(
    image_path: str,
    brightness_cut: int = 50,
    border_tol: float = 0.01,
    invert_thresh: int = 128,
) -> Tuple[str, Dict[str, float]]:
    """Realiza OCR em imagem de ultrassom.

    A função corta bordas escuras, inverte as cores caso o fundo seja preto e
    aplica o Tesseract para capturar o texto. Ao final, tenta identificar pares
    ``rotulo: valor`` em cada linha e retorna o texto cru e um dicionário com
    esses valores numéricos.

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
    Tuple[str, Dict[str, float]]
        Texto retornado pelo Tesseract e qualquer par ``rotulo: valor``
        encontrado.
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

    # 6. pares "rótulo-número"
    findings: Dict[str, float] = {}
    for line in raw_text.splitlines():
        match = re.search(
            r"([A-Za-z0-9]+)\s*[:=]?\s*([0-9]+[.,]?[0-9]*)", line)
        if match:
            key = match.group(1)
            value = float(match.group(2).replace(',', '.'))
            findings[key] = value

    return raw_text, findings
