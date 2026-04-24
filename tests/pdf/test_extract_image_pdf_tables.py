import sys
from types import SimpleNamespace

from PIL import Image

sys.modules.setdefault("pdf2image", SimpleNamespace(convert_from_path=lambda *args, **kwargs: []))

import ansimon_ai.pdf.extract_image_pdf as extract_image_pdf_module
from ansimon_ai.ocr.types import OCRResult, OCRSegment, OCRTable, OCRTableCell, OCRVertex


def test_extract_text_from_image_pdf_page_formats_table_output(monkeypatch) -> None:
    image = Image.new("RGB", (10, 10), "white")

    monkeypatch.setattr(
        extract_image_pdf_module,
        "convert_from_path",
        lambda _pdf_path, first_page=None, last_page=None: [image],
    )
    monkeypatch.setattr(
        extract_image_pdf_module,
        "ocr_image_to_result",
        lambda image_input, *, engine=None, lang=None: OCRResult(
            full_text="",
            segments=[
                OCRSegment(
                    text="약품명",
                    vertices=[
                        OCRVertex(x=0, y=0),
                        OCRVertex(x=10, y=0),
                        OCRVertex(x=10, y=10),
                        OCRVertex(x=0, y=10),
                    ],
                ),
                OCRSegment(
                    text="용량",
                    vertices=[
                        OCRVertex(x=12, y=0),
                        OCRVertex(x=22, y=0),
                        OCRVertex(x=22, y=10),
                        OCRVertex(x=12, y=10),
                    ],
                ),
            ],
            language="ko",
            engine="mock",
            tables=[
                OCRTable(
                    cells=[
                        OCRTableCell(
                            text="약품명",
                            row_index=0,
                            column_index=0,
                            vertices=[
                                OCRVertex(x=0, y=0),
                                OCRVertex(x=10, y=0),
                                OCRVertex(x=10, y=10),
                                OCRVertex(x=0, y=10),
                            ],
                        ),
                        OCRTableCell(
                            text="용량",
                            row_index=0,
                            column_index=1,
                            vertices=[
                                OCRVertex(x=12, y=0),
                                OCRVertex(x=22, y=0),
                                OCRVertex(x=22, y=10),
                                OCRVertex(x=12, y=10),
                            ],
                        ),
                    ]
                )
            ],
        ),
    )

    text = extract_image_pdf_module.extract_text_from_image_pdf_page("sample.pdf", 0)

    assert text == "약품명 | 용량"
