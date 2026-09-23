import os
import pytesseract
from PIL import Image
import pdfplumber

# Set Windows Tesseract OCR path fallback per requirement
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text_from_file(file_path: str, filename: str) -> str:
    """
    Extracts clinical text from uploaded PDF or Image files.
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        text_content = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content.append(extracted)
            return "\n".join(text_content).strip()
        except Exception as e:
            raise ValueError(f"Error parsing PDF file: {str(e)}")

    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        try:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image)
            return extracted_text.strip()
        except Exception as e:
            raise ValueError(f"Error performing OCR on image: {str(e)}. Make sure Tesseract OCR is installed.")

    elif ext in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    else:
        raise ValueError(f"Unsupported file format: {ext}. Please upload a PDF, PNG, JPG, or TXT file.")
