from ansimon_ai.structuring.anchor.apply import apply_anchors
from ansimon_ai.structuring.anchor.matcher import AnchorMatcher

def test_apply_anchor_success_single():
    matcher = AnchorMatcher()
    full_text = "그는 어제 밤에 전화했다."

    structuring = {
        "harassment": {
            "value": True,
            "evidence_span": "어제 밤에 전화했다",
        }
    }

    result = apply_anchors(
        structuring_result=structuring,
        full_text=full_text,
        matcher=matcher,
    )

    assert result["harassment"]["evidence_anchor"] == {
        "start_char": 3,
        "end_char": 13,
    }

def test_apply_anchor_null_when_not_found():
    matcher = AnchorMatcher()
    full_text = "그는 어제 밤에 전화했다."

    structuring = {
        "harassment": {
            "value": True,
            "evidence_span": "문자 보냈다",
        }
    }

    result = apply_anchors(
        structuring_result=structuring,
        full_text=full_text,
        matcher=matcher,
    )

    assert result["harassment"]["evidence_anchor"] is None

def test_apply_anchor_nested_list_and_dict():
    matcher = AnchorMatcher()
    full_text = "전화했다. 다시 전화했다."

    structuring = {
        "events": [
            {
                "type": "call",
                "evidence_span": "전화했다",
            }
        ]
    }

    result = apply_anchors(
        structuring_result=structuring,
        full_text=full_text,
        matcher=matcher,
    )

    assert result["events"][0]["evidence_anchor"] is None

def test_apply_does_not_mutate_input():
    matcher = AnchorMatcher()
    full_text = "그는 어제 밤에 전화했다."

    structuring = {
        "harassment": {
            "value": True,
            "evidence_span": "어제 밤에 전화했다",
        }
    }

    _ = apply_anchors(
        structuring_result=structuring,
        full_text=full_text,
        matcher=matcher,
    )

    assert "evidence_anchor" not in structuring["harassment"]