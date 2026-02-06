from ansimon_ai.structuring.tags.types import EvidenceTag
from ansimon_ai.validator.tag_validator_v0 import validate_evidence_tags_v0

def test_struct_invalid_is_fail():
    r = validate_evidence_tags_v0(
        tags=[
            EvidenceTag(tag="STRUCT_INVALID", source="structure", note="missing key"),
            EvidenceTag(tag="ANCHOR_NOT_FOUND", source="anchor"),
        ]
    )
    assert r.status.value == "fail"
    assert any(m.code == "E_STRUCT_INVALID" for m in r.messages)

def test_anchor_not_found_is_warn_when_structure_valid():
    r = validate_evidence_tags_v0(
        tags=[
            EvidenceTag(tag="STRUCT_VALID", source="structure"),
            EvidenceTag(tag="ANCHOR_NOT_FOUND", source="anchor"),
        ]
    )
    assert r.status.value == "warn"
    assert any(m.code == "W_ANCHOR_NOT_FOUND" for m in r.messages)


def test_anchor_ambiguous_is_warn_with_distinct_code():
    r = validate_evidence_tags_v0(
        tags=[
            EvidenceTag(tag="STRUCT_VALID", source="structure"),
            EvidenceTag(tag="ANCHOR_AMBIGUOUS", source="anchor", note="multiple matches"),
        ]
    )
    assert r.status.value == "warn"
    assert any(m.code == "W_ANCHOR_AMBIGUOUS" for m in r.messages)

def test_confidence_without_anchor_is_warn():
    r = validate_evidence_tags_v0(
        tags=[
            EvidenceTag(tag="STRUCT_VALID", source="structure"),
            EvidenceTag(tag="ANCHOR_OK", source="anchor"),
            EvidenceTag(tag="CONFIDENCE_PRESENT", source="confidence"),
            EvidenceTag(tag="CONFIDENCE_WITHOUT_ANCHOR", source="confidence"),
        ]
    )
    assert r.status.value == "warn"
    assert any(m.code == "W_CONFIDENCE_WITHOUT_ANCHOR" for m in r.messages)

def test_happy_path_is_pass():
    r = validate_evidence_tags_v0(
        tags=[
            EvidenceTag(tag="STRUCT_VALID", source="structure"),
            EvidenceTag(tag="ANCHOR_OK", source="anchor"),
            EvidenceTag(tag="CONFIDENCE_PRESENT", source="confidence"),
        ]
    )
    assert r.status.value == "pass"
    assert r.messages == []

def test_empty_tags_is_warn():
    r = validate_evidence_tags_v0(tags=[])
    assert r.status.value == "warn"
    assert any(m.code == "W_NO_TAGS" for m in r.messages)