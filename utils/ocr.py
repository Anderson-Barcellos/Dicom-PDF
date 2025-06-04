import pytesseract
from PIL import Image

def extract_ultrasound_text(image_path: str) -> str:
    """Extract text from an ultrasound image using pytesseract."""
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

