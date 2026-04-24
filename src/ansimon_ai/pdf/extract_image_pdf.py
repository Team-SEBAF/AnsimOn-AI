from typing import List, Optional
from pdf2image import convert_from_path

from ansimon_ai.ocr.from_ocr import ocr_image_to_result

def extract_text_from_image_pdf(
    pdf_path: str,
    lang: str = "kor",
    engine: Optional[str] = None,
) -> List[str]:
    images = convert_from_path(pdf_path)
    texts = []
    for img in images:
        result = ocr_image_to_result(img, engine=engine, lang=lang)
        texts.append(result.full_text)
    return texts

def extract_text_from_image_pdf_page(
    pdf_path: str,
    page_index: int,
    lang: str = "kor",
    engine: Optional[str] = None,
) -> str:
    images = convert_from_path(
        pdf_path,
        first_page=page_index + 1,
        last_page=page_index + 1,
    )
    if not images:
        return ""
    result = ocr_image_to_result(images[0], engine=engine, lang=lang)
    return result.full_text