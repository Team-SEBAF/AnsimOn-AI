import os
import pytest

from ansimon_ai.ocr.types import OCRSegment, OCRResult
from ansimon_ai.ocr.from_ocr import build_structuring_input_from_ocr, ocr_image_to_result
from ansimon_ai.structuring.tag_patterns import extract_tags_from_structuring_input

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

def test_build_structuring_input_from_ocr_cleans_chat_ui_noise():
    segments = [
        OCRSegment(text="< 가해자 Q ="),
        OCRSegment(text="2026 년 3 월 10 일 화요일 >"),
        OCRSegment(text="+ - 글"),
        OCRSegment(text="@…"),
        OCRSegment(text="불 켜져 있는 것 같은데"),
    ]
    full_text = "\n".join(segment.text for segment in segments)

    struct_input = build_structuring_input_from_ocr(make_ocr_result(segments, full_text))

    assert "가해자 Q" not in struct_input.full_text
    assert "<" not in struct_input.full_text
    assert "=" not in struct_input.full_text
    assert "+ - 글" not in struct_input.full_text
    assert "@…" not in struct_input.full_text
    assert "가해자" in struct_input.full_text
    assert "불 켜져 있는 것 같은데" in struct_input.full_text

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
    not os.path.exists("D:\\sample2.png"),
    reason="예시 이미지 파일이 존재하지 않음"
)

def test_ocr_image_integration():
    image_path = "D:\\sample2.png"
    if not os.path.exists(image_path):
        pytest.skip(f"테스트 이미지 없음: {image_path}")
    result = ocr_image_to_result(image_path)
    print(result)
    assert hasattr(result, "full_text")
    assert hasattr(result, "segments")
    assert isinstance(result.segments, list)

def test_tag_extraction_threat():
    segments = [
        OCRSegment(text="2024.06.01 15:20 김철수: 너 오늘 집에 안 들어오면 가만 안 둘 거야."),
        OCRSegment(text="2024.06.01 15:21 김철수: 경찰에 신고해봐야 소용없어."),
        OCRSegment(text="2024.06.01 15:22 김철수: 네가 한 일 다 알고 있어."),
    ]
    full_text = " ".join([s.text for s in segments])
    struct_input = build_structuring_input_from_ocr(make_ocr_result(segments, full_text))
    tags = extract_tags_from_structuring_input(struct_input)
    assert "threat" in tags

def test_tag_extraction_sexual():
    segments = [
        OCRSegment(text="오늘따라 야하다"),
        OCRSegment(text="가슴이 참 예쁘네"),
        OCRSegment(text="야한 사진 보내줘"),
    ]
    full_text = " ".join([s.text for s in segments])
    struct_input = build_structuring_input_from_ocr(make_ocr_result(segments, full_text))
    tags = extract_tags_from_structuring_input(struct_input)
    assert "sexual_insult" in tags

def test_tag_extraction_refusal():
    segments = [
        OCRSegment(text="그만해"),
        OCRSegment(text="연락하지 말라"),
        OCRSegment(text="싫다"),
    ]
    full_text = " ".join([s.text for s in segments])
    struct_input = build_structuring_input_from_ocr(make_ocr_result(segments, full_text))
    tags = extract_tags_from_structuring_input(struct_input)
    assert "refusal" in tags