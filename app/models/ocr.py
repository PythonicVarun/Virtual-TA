import base64
import io
from PIL import Image
import pytesseract


class OCR:
    def __init__(self):
        pass

    def extract_text(self, image_data: str) -> str:
        try:
            img_data = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(img_data))
            return pytesseract.image_to_string(img)
        except Exception as e:
            raise ValueError(f"OCR decoding error: {e}")
