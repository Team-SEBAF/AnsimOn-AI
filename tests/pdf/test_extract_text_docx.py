from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from zipfile import ZipFile
from PIL import Image

import ansimon_ai.pdf.extract_text_docx as extract_text_docx_module
from ansimon_ai.ocr.types import OCRResult, OCRSegment


TEST_TMP_DIR = Path("data/_pdf_test_tmp")

def _write_docx_with_images() -> Path:
    TEST_TMP_DIR.mkdir(parents=True, exist_ok=True)
    docx_path = TEST_TMP_DIR / f"{uuid4()}-sample.docx"
    image_buffer = BytesIO()
    Image.new("RGB", (12, 12), "white").save(image_buffer, format="PNG")

    with ZipFile(docx_path, "w") as archive:
        archive.writestr("word/document.xml", "<document />")
        archive.writestr("word/media/image1.png", image_buffer.getvalue())
        archive.writestr("word/media/notes.txt", b"not-an-image")

    return docx_path

def test_extract_text_from_docx_images_uses_shared_ocr_runner(monkeypatch):
    docx_path = _write_docx_with_images()

    def fake_ocr_image_to_result(image_input, *, engine=None, lang=None):
        assert isinstance(image_input, Image.Image)
        assert engine == "clova"
        assert lang == "kor"
        return OCRResult(
            full_text="line one\nline two",
            segments=[
                OCRSegment(text="line one"),
                OCRSegment(text="line two"),
            ],
            language="ko",
            engine="mock",
        )

    monkeypatch.setattr(
        extract_text_docx_module,
        "ocr_image_to_result",
        fake_ocr_image_to_result,
    )

    texts = extract_text_docx_module._extract_text_from_docx_images(
        str(docx_path),
        engine="clova",
    )

    assert texts == ["line one", "line two"]

def test_extract_text_from_docx_combines_text_table_and_image_ocr(monkeypatch):
    docx_path = _write_docx_with_images()

    fake_document = SimpleNamespace(
        paragraphs=[
            SimpleNamespace(text="  first paragraph  "),
            SimpleNamespace(text=""),
        ],
        tables=[
            SimpleNamespace(
                rows=[
                    SimpleNamespace(
                        cells=[
                            SimpleNamespace(text="cell A"),
                            SimpleNamespace(text="cell B"),
                        ]
                    )
                ]
            )
        ],
    )

    fake_docx_module = SimpleNamespace(Document=lambda _path: fake_document)
    monkeypatch.setitem(__import__("sys").modules, "docx", fake_docx_module)

    monkeypatch.setattr(
        extract_text_docx_module,
        "ocr_image_to_result",
        lambda image_input, *, engine=None, lang=None: OCRResult(
            full_text="image ocr text",
            segments=[OCRSegment(text="image ocr text")],
            language="ko",
            engine="mock",
        ),
    )

    text = extract_text_docx_module.extract_text_from_docx(
        str(docx_path),
        engine="clova",
    )

    assert text == "first paragraph\ncell A | cell B\nimage ocr text"