from ansimon_ai.requirements.state_v0 import (
    RequirementState,
    evaluate_requirement_state_v0,
)
from ansimon_ai.structuring.tags.types import EvidenceTag
from ansimon_ai.validator.tag_validator_v0 import validate_evidence_tags_v0

def test_evaluable_when_no_warnings():
    tags = [
        EvidenceTag(tag="STRUCT_VALID", source="structure"),
        EvidenceTag(tag="ANCHOR_OK", source="anchor"),
        EvidenceTag(tag="CONFIDENCE_PRESENT", source="confidence"),
    ]
    r = evaluate_requirement_state_v0(tags=tags)
    assert r.state == RequirementState.EVALUATABLE
    assert r.reason_codes == []

def test_unstable_when_anchor_not_found():
    tags = [
        EvidenceTag(tag="STRUCT_VALID", source="structure"),
        EvidenceTag(tag="ANCHOR_NOT_FOUND", source="anchor"),
    ]
    r = evaluate_requirement_state_v0(tags=tags)
    assert r.state == RequirementState.UNSTABLE
    assert "W_ANCHOR_NOT_FOUND" in r.reason_codes

def test_unstable_when_anchor_ambiguous():
    tags = [
        EvidenceTag(tag="STRUCT_VALID", source="structure"),
        EvidenceTag(tag="ANCHOR_AMBIGUOUS", source="anchor"),
    ]
    r = evaluate_requirement_state_v0(tags=tags)
    assert r.state == RequirementState.UNSTABLE
    assert "W_ANCHOR_AMBIGUOUS" in r.reason_codes

def test_invalid_when_struct_invalid():
    tags = [
        EvidenceTag(tag="STRUCT_INVALID", source="structure", note="missing key"),
        EvidenceTag(tag="ANCHOR_OK", source="anchor"),
    ]
    r = evaluate_requirement_state_v0(tags=tags)
    assert r.state == RequirementState.INVALID
    assert "E_STRUCT_INVALID" in r.reason_codes

def test_accepts_explicit_tag_validation_result():
    tags = [
        EvidenceTag(tag="STRUCT_VALID", source="structure"),
        EvidenceTag(tag="ANCHOR_NOT_FOUND", source="anchor"),
    ]
    tag_validation = validate_evidence_tags_v0(tags=tags)
    r = evaluate_requirement_state_v0(tags=tags, tag_validation=tag_validation)
    assert r.state == RequirementState.UNSTABLE
    assert r.reason_codes == [m.code for m in tag_validation.messages]