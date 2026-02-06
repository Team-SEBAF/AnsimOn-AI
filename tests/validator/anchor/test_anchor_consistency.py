from ansimon_ai.validator.runner import ValidatorRunner
from ansimon_ai.validator.rules.anchor_consistency import (
    validate_anchor_consistency,
)

BASE = {
    "evidence_metadata": {
        "value": {},
        "confidence": "low",
        "evidence_span": None,
        "evidence_anchor": None,
    },
    "parties": {
        "value": {},
        "confidence": "low",
        "evidence_span": None,
        "evidence_anchor": None,
    },
}

def run(data):
    runner = ValidatorRunner([validate_anchor_consistency])
    return runner.run(data)

def test_anchor_without_span_fail():
    bad = dict(BASE)
    bad["parties"] = {
        "value": {},
        "confidence": "high",
        "evidence_span": None,
        "evidence_anchor": {
            "modality": "text",
            "start_char": 0,
            "end_char": 3,
        },
    }

    r = run(bad)
    assert r.status.value == "fail"

def test_span_without_anchor_pass():
    good = dict(BASE)
    good["parties"] = {
        "value": {},
        "confidence": "high",
        "evidence_span": "전남친이",
        "evidence_anchor": None,
    }

    r = run(good)
    assert r.status.value == "pass"

def test_anchor_start_end_invalid_fail():
    bad = dict(BASE)
    bad["parties"] = {
        "value": {},
        "confidence": "high",
        "evidence_span": "전남친이",
        "evidence_anchor": {
            "modality": "text",
            "start_char": 5,
            "end_char": 5,
        },
    }

    r = run(bad)
    assert r.status.value == "fail"