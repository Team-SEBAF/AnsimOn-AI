from ansimon_ai.validator.runner import ValidatorRunner
from ansimon_ai.validator.rules.confidence.confidence_value import (
    validate_confidence_value,
)

BASE = {
    "evidence_metadata": {
        "confidence": "low",
        "evidence_span": None,
        "evidence_anchor": None,
    },
    "parties": {
        "confidence": "medium",
        "evidence_span": "전남친이",
        "evidence_anchor": None,
    },
}

def test_confidence_valid_pass():
    runner = ValidatorRunner([validate_confidence_value])
    r = runner.run(BASE)

    assert r.status.value == "pass"

def test_confidence_invalid_value_fail():
    bad = dict(BASE)
    bad["parties"] = {
        "confidence": "very_high",
        "evidence_span": "전남친이",
        "evidence_anchor": None,
    }

    runner = ValidatorRunner([validate_confidence_value])
    r = runner.run(bad)

    assert r.status.value == "fail"
    assert any(m.code == "confidence_invalid_value" for m in r.messages)

def test_confidence_missing_fail():
    bad = dict(BASE)
    bad["parties"] = {
        "evidence_span": "전남친이",
        "evidence_anchor": None,
    }

    runner = ValidatorRunner([validate_confidence_value])
    r = runner.run(bad)

    assert r.status.value == "fail"
    assert any(m.code == "confidence_missing" for m in r.messages)

def test_confidence_high_requires_evidence_span_fail():
    bad = dict(BASE)
    bad["parties"] = {
        "confidence": "high",
        "evidence_span": None,
        "evidence_anchor": None,
    }

    runner = ValidatorRunner([validate_confidence_value])
    r = runner.run(bad)

    assert r.status.value == "fail"
    assert any(
        m.code == "confidence_high_requires_evidence" for m in r.messages
    )

def test_confidence_high_with_evidence_pass():
    good = dict(BASE)
    good["parties"] = {
        "confidence": "high",
        "evidence_span": "전남친이",
        "evidence_anchor": None,
    }

    runner = ValidatorRunner([validate_confidence_value])
    r = runner.run(good)

    assert r.status.value == "pass"