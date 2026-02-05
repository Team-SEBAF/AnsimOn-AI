from ansimon_ai.structuring.tags.generate import generate_evidence_tags
from tests.structuring.tags._helpers import make_result

def test_tags_anchor_not_found():
    result = make_result(
        matched=0,
        unmatched=1,
        output_json={"event": {}},
    )

    tags = generate_evidence_tags(result=result)
    tag_names = {t.tag for t in tags}

    assert "ANCHOR_NOT_FOUND" in tag_names
    assert "STRUCT_VALID" in tag_names
    assert "CONFIDENCE_PRESENT" not in tag_names