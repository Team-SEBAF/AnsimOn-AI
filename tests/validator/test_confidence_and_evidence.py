from ansimon_ai.validator.runner import ValidatorRunner
from ansimon_ai.validator.rules.schema.confidence_and_evidence import (
    validate_confidence_and_evidence
)

def test_invalid_confidence_fails():
    data = {
        "field": {
            "confidence": "sure",
            "evidence_span": None,
            "evidence_anchor": None,
        }
    }
    runner = ValidatorRunner([validate_confidence_and_evidence])
    r = runner.run(data)
    assert r.status.value == "fail"

def test_span_null_anchor_not_null_fails():
    data = {
        "field": {
            "confidence": "low",
            "evidence_span": None,
            "evidence_anchor": {"modality": "text", "start_char": 0, "end_char": 1},
        }
    }
    runner = ValidatorRunner([validate_confidence_and_evidence])
    r = runner.run(data)
    assert r.status.value == "fail"

def test_valid_pair_pass():
    data = {
        "field": {
            "confidence": "high",
            "evidence_span": "abc",
            "evidence_anchor": {"modality": "text", "start_char": 0, "end_char": 3},
        }
    }
    runner = ValidatorRunner([validate_confidence_and_evidence])
    r = runner.run(data)
    assert r.status.value == "pass"