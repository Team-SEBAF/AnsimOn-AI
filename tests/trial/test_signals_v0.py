from ansimon_ai.structuring.types import AnchorStats, StructuringResult, ValidationResult
from ansimon_ai.structuring.tags.types import EvidenceTag
from ansimon_ai.trial.signals_v0.generate import (
    generate_trial_signals_v0_from_text,
    generate_trial_signals_v0_from_structuring,
)
from ansimon_ai.trial.signals_v0.validate import validate_trial_signals_output_v0
from ansimon_ai.validator.result import ValidationStatus

def test_trial_signals_v0_text_mode_smoke():
    text = """
    연락하지 마.
    연락하지 마.
    연락하지 마.
    찾아가겠다.
    """.strip()

    out = generate_trial_signals_v0_from_text(full_text=text)

    assert out.mode == "text"
    assert out.version == "v0"

    names = {s.name for s in out.signals}
    assert names == {"repetition", "threat", "refusal"}

    rep = next(s for s in out.signals if s.name == "repetition")
    thr = next(s for s in out.signals if s.name == "threat")
    ref = next(s for s in out.signals if s.name == "refusal")

    assert rep.level in {"부족", "경고", "충분"}
    assert thr.level in {"부족", "경고", "충분"}
    assert ref.level in {"부족", "경고", "충분"}

    # refusal/threat should have at least one evidence span in this sample
    assert thr.level == "충분"
    assert ref.level == "충분"
    assert thr.evidence and thr.evidence[0].evidence_span
    assert ref.evidence and ref.evidence[0].evidence_span

    v = validate_trial_signals_output_v0(output=out)
    assert v.status in {ValidationStatus.PASS, ValidationStatus.WARN}

def test_trial_signals_v0_text_mode_no_matches_is_explained():
    text = "안녕하세요. 오늘 날씨가 좋네요.".strip()

    out = generate_trial_signals_v0_from_text(full_text=text)
    assert out.mode == "text"

    for s in out.signals:
        assert s.reason_codes
        assert len(s.evidence) >= 0

    v = validate_trial_signals_output_v0(output=out)
    assert v.status in {ValidationStatus.PASS, ValidationStatus.WARN}

def test_trial_signals_v0_text_mode_repetition_x2_is_warning_and_has_evidence():
    out = generate_trial_signals_v0_from_text(full_text="abcd abcd")
    rep = next(s for s in out.signals if s.name == "repetition")

    assert rep.level == "경고"
    assert rep.reason_codes
    assert rep.evidence and rep.evidence[0].evidence_span

def test_trial_signals_v0_evidence_mode_smoke_safe():
    output_json = {
        "frequency": {
            "value": "거의 매일",
            "confidence": "high",
            "evidence_span": "거의 매일",
            "evidence_anchor": {"modality": "text", "start_char": 10, "end_char": 14},
        },
        "refusal_signal": {
            "value": "그만",
            "confidence": "high",
            "evidence_span": "그만",
            "evidence_anchor": {"modality": "text", "start_char": 20, "end_char": 22},
        },
    }

    result = StructuringResult(
        output_json=output_json,
        cache_hit=False,
        anchor_stats=AnchorStats(
            total_spans=2,
            matched_spans=2,
            partial_matched_spans=0,
            unmatched_spans=0,
        ),
        validation=ValidationResult(status="PASS", error_codes=[], message=None),
        run_id="test",
    )

    tags = [
        EvidenceTag(tag="ANCHOR_OK", source="anchor"),
        EvidenceTag(tag="STRUCT_VALID", source="structure"),
        EvidenceTag(tag="CONFIDENCE_PRESENT", source="confidence"),
    ]

    out = generate_trial_signals_v0_from_structuring(result=result, tags=tags, max_evidence=3)

    assert out.mode == "evidence"
    assert out.version == "v0"

    names = {s.name for s in out.signals}
    assert names == {"evidence_strength", "clarity", "safety"}

    strength = next(s for s in out.signals if s.name == "evidence_strength")
    clarity = next(s for s in out.signals if s.name == "clarity")
    safety = next(s for s in out.signals if s.name == "safety")

    assert strength.level == "안전"
    assert clarity.level == "안전"
    assert safety.level == "안전"

    for s in out.signals:
        assert len(s.evidence) <= 3

    v = validate_trial_signals_output_v0(output=out)
    assert v.status in {ValidationStatus.PASS, ValidationStatus.WARN}

def test_trial_signals_v0_evidence_mode_struct_invalid_is_risky():
    result = StructuringResult(
        output_json={},
        cache_hit=False,
        anchor_stats=AnchorStats(
            total_spans=0,
            matched_spans=0,
            partial_matched_spans=0,
            unmatched_spans=0,
        ),
        validation=ValidationResult(status="FAIL", error_codes=["x"], message="bad"),
        run_id="test",
    )

    tags = [
        EvidenceTag(tag="STRUCT_INVALID", source="structure", note="bad"),
        EvidenceTag(tag="ANCHOR_NOT_FOUND", source="anchor"),
    ]

    out = generate_trial_signals_v0_from_structuring(result=result, tags=tags, max_evidence=3)
    strength = next(s for s in out.signals if s.name == "evidence_strength")
    clarity = next(s for s in out.signals if s.name == "clarity")
    safety = next(s for s in out.signals if s.name == "safety")

    assert strength.reason_codes
    assert "E_NO_EVIDENCE_POOL" in strength.reason_codes
    assert not strength.evidence

    assert clarity.reason_codes
    assert not clarity.evidence

    assert safety.level == "위험"

    v = validate_trial_signals_output_v0(output=out)
    assert v.status in {ValidationStatus.PASS, ValidationStatus.WARN}