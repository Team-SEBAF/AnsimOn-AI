from ansimon_ai.ocr.clova_ocr import _parse_clova_ocr_response
from ansimon_ai.ocr.layout import assign_speaker_sides
from ansimon_ai.ocr.from_ocr import ocr_image_to_result
from ansimon_ai.ocr.types import OCRResult, OCRSegment, OCRVertex

def test_parse_clova_ocr_response_builds_line_segments():
    result = _parse_clova_ocr_response(
        {
            "lang": "ko",
            "images": [
                {
                    "fields": [
                        {
                            "inferText": "안녕",
                            "lineBreak": False,
                            "boundingPoly": {
                                "vertices": [
                                    {"x": 0, "y": 0},
                                    {"x": 10, "y": 0},
                                    {"x": 10, "y": 10},
                                    {"x": 0, "y": 10},
                                ]
                            },
                        },
                        {
                            "inferText": "하세요",
                            "lineBreak": True,
                            "boundingPoly": {
                                "vertices": [
                                    {"x": 11, "y": 0},
                                    {"x": 20, "y": 0},
                                    {"x": 20, "y": 10},
                                    {"x": 11, "y": 10},
                                ]
                            },
                        },
                        {
                            "inferText": "테스트",
                            "lineBreak": True,
                            "boundingPoly": {
                                "vertices": [
                                    {"x": 0, "y": 20},
                                    {"x": 20, "y": 20},
                                    {"x": 20, "y": 30},
                                    {"x": 0, "y": 30},
                                ]
                            },
                        },
                    ]
                }
            ],
        }
    )

    assert result.engine == "clova:v2"
    assert result.language == "ko"
    assert result.full_text == "안녕 하세요\n테스트"
    assert len(result.segments) == 2
    assert result.segments[0].text == "안녕 하세요"
    assert result.segments[0].vertices is not None
    assert len(result.segments[0].vertices) == 8
    assert result.segments[0].speaker_side == "unknown"

def test_ocr_image_to_result_uses_clova_when_engine_env_is_set(monkeypatch):
    expected = object()

    monkeypatch.setenv("OCR_ENGINE", "clova")
    monkeypatch.setattr(
        "ansimon_ai.ocr.from_ocr.clova_ocr_image_to_result",
        lambda image_path: expected,
    )

    assert ocr_image_to_result("dummy.png") is expected


def test_ocr_segment_coordinate_properties():
    segment = OCRSegment(
        text="안녕하세요",
        vertices=[
            OCRVertex(x=10, y=20),
            OCRVertex(x=50, y=20),
            OCRVertex(x=50, y=60),
            OCRVertex(x=10, y=60),
        ],
    )

    assert segment.min_x == 10
    assert segment.max_x == 50
    assert segment.center_x == 30
    assert segment.min_y == 20
    assert segment.max_y == 60
    assert segment.center_y == 40

def test_assign_speaker_sides_marks_left_right_and_unknown():
    result = assign_speaker_sides(
        OCRResult(
            full_text="left\nmiddle\nright",
            engine="clova:v2",
            segments=[
                OCRSegment(
                    text="left",
                    vertices=[
                        OCRVertex(x=0, y=0),
                        OCRVertex(x=100, y=0),
                        OCRVertex(x=100, y=20),
                        OCRVertex(x=0, y=20),
                    ],
                ),
                OCRSegment(
                    text="middle",
                    vertices=[
                        OCRVertex(x=140, y=0),
                        OCRVertex(x=180, y=0),
                        OCRVertex(x=180, y=20),
                        OCRVertex(x=140, y=20),
                    ],
                ),
                OCRSegment(
                    text="right",
                    vertices=[
                        OCRVertex(x=220, y=0),
                        OCRVertex(x=320, y=0),
                        OCRVertex(x=320, y=20),
                        OCRVertex(x=220, y=20),
                    ],
                ),
            ],
        )
    )

    assert result.segments[0].speaker_side == "left"
    assert result.segments[1].speaker_side == "unknown"
    assert result.segments[2].speaker_side == "right"