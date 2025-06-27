import os
import sys

# Ensure project root is on sys.path so local modules can be imported
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def test_imports():
    import IMG2PDF
    from DicomManager.DICOM import DICOM2JPEG
    from DicomManager.unzip import Unzipper
    from PDFMAKER.pdfmaker import MkPDF

    assert callable(IMG2PDF.Make_PDF)
    assert callable(DICOM2JPEG)
    assert callable(Unzipper)
    assert callable(MkPDF)
