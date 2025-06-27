import os
import sys
import numpy as np
import cv2
from unittest import mock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.ocr import extract_ultrasound_text


def test_import_extract_ultrasound_text():
    assert callable(extract_ultrasound_text)


def test_extract_parses_text(tmp_path):
    img = np.full((10, 10), 255, dtype=np.uint8)
    img_path = tmp_path / "img.png"
    cv2.imwrite(str(img_path), img)
    sample = "BPD: 45.0\nFL 23,5\nAC=120.0"
    with mock.patch("pytesseract.image_to_string", return_value=sample):
        _, findings = extract_ultrasound_text(str(img_path))
    assert findings == {"BPD": 45.0, "FL": 23.5, "AC": 120.0}
