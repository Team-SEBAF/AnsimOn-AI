from ansimon_ai.requirements.event_io_v0 import (
    evaluate_event_io_contract_v0,
    run_requirement_service_v0,
)
from ansimon_ai.requirements.state_v0 import (
    RequirementState,
    RequirementStateResult,
)
from ansimon_ai.structuring.tags.types import EvidenceTag

def test_event_contract_invalid_denies_event():
    r = RequirementStateResult(state=RequirementState.INVALID, reason_codes=["E_STRUCT_INVALID"])
    out = evaluate_event_io_contract_v0(requirement_state=r)
    assert out.can_create_event is False
    assert out.policy == "deny"
    assert out.caution_tag is None
    assert "E_STRUCT_INVALID" in out.reason_codes

def test_event_contract_unstable_allows_with_caution():
    r = RequirementStateResult(
        state=RequirementState.UNSTABLE, reason_codes=["W_ANCHOR_NOT_FOUND"]
    )
    out = evaluate_event_io_contract_v0(requirement_state=r)
    assert out.can_create_event is True
    assert out.policy == "allow_with_caution"
    assert out.caution_tag == "UNSTABLE"
    assert "W_ANCHOR_NOT_FOUND" in out.reason_codes

def test_event_contract_evaluable_allows():
    r = RequirementStateResult(state=RequirementState.EVALUATABLE, reason_codes=[])
    out = evaluate_event_io_contract_v0(requirement_state=r)
    assert out.can_create_event is True
    assert out.policy == "allow"
    assert out.caution_tag is None
    assert out.reason_codes == []

def test_service_entrypoint_computes_state_and_event_policy():
    evidence = {"_note": "dummy"}
    tags = [
        EvidenceTag(tag="STRUCT_VALID", source="structure"),
        EvidenceTag(tag="ANCHOR_NOT_FOUND", source="anchor"),
    ]

    out = run_requirement_service_v0(evidence=evidence, tags=tags)
    assert out.requirement_state.state == RequirementState.UNSTABLE
    assert "W_ANCHOR_NOT_FOUND" in out.requirement_state.reason_codes
    assert out.event_io.policy == "allow_with_caution"
    assert out.event_io.caution_tag == "UNSTABLE"