import pytest
from ansimon_ai.pdf.extract_text_auto import extract_text_auto

@pytest.mark.parametrize("pdf_path", [
    r"D:\Project\AnsimOn\진료기록_이미지.pdf",
    r"D:\Project\AnsimOn\진료기록부.pdf",
])
def test_extract_text_auto(pdf_path):
    texts = extract_text_auto(pdf_path)
    assert isinstance(texts, list)
    assert all(isinstance(t, str) for t in texts)
    assert any(len(t.strip()) > 0 for t in texts)