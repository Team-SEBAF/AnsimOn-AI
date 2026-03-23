import os
import pytest

pytest.importorskip("pdfplumber")

from ansimon_ai.pdf.extract_text_auto import extract_text_auto
import ansimon_ai.pdf.extract_text_auto as extract_text_auto_module

@pytest.mark.parametrize(
    "pdf_path",
    [
        r"D:\Project\AnsimOn\진료기록_이미지.pdf",
        r"D:\Project\AnsimOn\진료기록부.pdf",
    ],
)
def test_extract_text_auto(pdf_path):
    if not os.path.exists(pdf_path):
        pytest.skip(f"테스트용 PDF 파일이 없습니다: {pdf_path}")

    texts = extract_text_auto(pdf_path)
    assert isinstance(texts, list)
    assert all(isinstance(t, str) for t in texts)
    assert any(len(t.strip()) > 0 for t in texts)

def test_extract_text_auto_handles_mixed_pdf(monkeypatch):
    monkeypatch.setattr(extract_text_auto_module, "detect_pdf_type", lambda _pdf_path: ("text", 1))
    monkeypatch.setattr(
        extract_text_auto_module,
        "detect_pdf_page_types",
        lambda _pdf_path: ["text", "image", "text"],
    )
    monkeypatch.setattr(
        extract_text_auto_module,
        "extract_text_from_pdf_page",
        lambda _pdf_path, page_index: f"text-page-{page_index}",
    )
    monkeypatch.setattr(
        extract_text_auto_module,
        "extract_text_from_image_pdf_page",
        lambda _pdf_path, page_index, lang="kor": f"ocr-page-{page_index}-{lang}",
    )

    texts = extract_text_auto("mixed.pdf")

    assert texts == [
        "text-page-0",
        "ocr-page-1-kor",
        "text-page-2",
    ]