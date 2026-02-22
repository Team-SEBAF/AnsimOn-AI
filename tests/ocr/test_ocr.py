import os
import pytest
from PIL import Image

from ansimon_ai.ocr.types import OCRSegment, OCRResult
from ansimon_ai.ocr.from_ocr import build_structuring_input_from_ocr, ocr_image_to_result

def make_ocr_result(segments, full_text):
    return OCRResult(
        full_text=full_text,
        segments=segments,
        language="ko",
        engine="mock"
    )

def test_threat_kakao():
    segments = [
        OCRSegment(text="2024.06.01 15:20\n김철수: 너 오늘 집에 안 들어오면 가만 안 둘 거야.", page=1, line=1),
        OCRSegment(text="2024.06.01 15:21\n김철수: 경찰에 신고해봐야 소용없어.", page=1, line=2),
        OCRSegment(text="2024.06.01 15:22\n김철수: 네가 한 일 다 알고 있어.", page=1, line=3),
    ]
    full_text = "2024.06.01 15:20 김철수: 너 오늘 집에 안 들어오면 가만 안 둘 거야. 2024.06.01 15:21 김철수: 경찰에 신고해봐야 소용없어. 2024.06.01 15:22 김철수: 네가 한 일 다 알고 있어."
    struct_input = build_structuring_input_from_ocr(make_ocr_result(segments, full_text))
    assert len(struct_input.segments) == 3
    assert "협박" not in struct_input.full_text

def test_missed_calls():
    segments = [
        OCRSegment(text="2024.06.01 13:10 부재중 전화 (홍길동)", page=1, line=1),
        OCRSegment(text="2024.06.01 13:12 부재중 전화 (홍길동)", page=1, line=2),
        OCRSegment(text="2024.06.01 14:00 부재중 전화 (홍길동)", page=1, line=3),
    ]
    full_text = "2024.06.01 13:10 부재중 전화 (홍길동) 2024.06.01 13:12 부재중 전화 (홍길동) 2024.06.01 14:00 부재중 전화 (홍길동)"
    struct_input = build_structuring_input_from_ocr(make_ocr_result(segments, full_text))
    assert len(struct_input.segments) == 3
    assert "부재중" in struct_input.full_text

def test_medical_record():
    segments = [
        OCRSegment(text="진단명: 외상성 스트레스 장애", page=1, line=1),
        OCRSegment(text="진단일: 2024년 6월 2일", page=1, line=2),
        OCRSegment(text="환자명: 홍길동", page=1, line=3),
        OCRSegment(text="의사: 박의사", page=1, line=4),
    ]
    full_text = "진단명: 외상성 스트레스 장애 진단일: 2024년 6월 2일 환자명: 홍길동 의사: 박의사"
    struct_input = build_structuring_input_from_ocr(make_ocr_result(segments, full_text))
    assert "스트레스 장애" in struct_input.full_text
    assert len(struct_input.segments) == 4

def test_counseling_record():
    segments = [
        OCRSegment(text="2024.06.01 16:00 상담센터: 피해자가 심리적 불안 호소", page=1, line=1),
        OCRSegment(text="2024.06.01 16:10 상담센터: 가족과의 갈등 언급", page=1, line=2),
    ]
    full_text = "2024.06.01 16:00 상담센터: 피해자가 심리적 불안 호소 2024.06.01 16:10 상담센터: 가족과의 갈등 언급"
    struct_input = build_structuring_input_from_ocr(make_ocr_result(segments, full_text))
    assert "불안" in struct_input.full_text
    assert len(struct_input.segments) == 2

@pytest.mark.skipif(
    not os.path.exists("D:\\sample.png"),
    reason="예시 이미지 파일이 존재하지 않음"
)

def test_ocr_image_integration():
    image_path = "D:\\sample.png"
    if not os.path.exists(image_path):
        pytest.skip(f"테스트 이미지 없음: {image_path}")
    result = ocr_image_to_result(image_path)
    print(result)
    assert hasattr(result, "full_text")
    assert hasattr(result, "segments")
    assert isinstance(result.segments, list)