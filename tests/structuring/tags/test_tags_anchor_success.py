from ansimon_ai.structuring.tags.generate import generate_evidence_tags
from tests.structuring.tags._helpers import make_result

def test_tags_anchor_ok():
    result = make_result(
        matched=1,
        unmatched=0,
        output_json={"event": {"confidence": "high"}},
    )

    tags = generate_evidence_tags(result=result)
    tag_names = {t.tag for t in tags}

    assert "ANCHOR_OK" in tag_names
    assert "STRUCT_VALID" in tag_names
    assert "CONFIDENCE_PRESENT" in tag_names
    assert "CONFIDENCE_WITHOUT_ANCHOR" not in tag_names