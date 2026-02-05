from ansimon_ai.structuring.tags.generate import generate_evidence_tags
from tests.structuring.tags._helpers import make_result

def test_tags_confidence_without_anchor():
    result = make_result(
        matched=0,
        unmatched=1,
        output_json={
            "event": {
                "confidence": "high",
            }
        },
    )

    tags = generate_evidence_tags(result=result)
    tag_names = {t.tag for t in tags}

    assert "CONFIDENCE_PRESENT" in tag_names
    assert "CONFIDENCE_WITHOUT_ANCHOR" in tag_names