from ansimon_ai.validator.rules.required_keys import validate_required_keys

def minimal_valid_doc():
    base = {
        "value": None,
        "confidence": "low",
        "evidence_span": None,
        "evidence_anchor": None,
    }
    return {
        "evidence_metadata": base.copy(),
        "parties": base.copy(),
        "period": base.copy(),
        "frequency": base.copy(),
        "channel": base.copy(),
        "locations": base.copy(),
        "action_types": base.copy(),
        "refusal_signal": base.copy(),
        "threat_indicators": base.copy(),
        "impact_on_victim": base.copy(),
        "report_or_record": base.copy(),
    }

def test_pass_minimal():
    errors = validate_required_keys(minimal_valid_doc())
    assert errors == []

def test_missing_top_key():
    doc = minimal_valid_doc()
    doc.pop("period")
    errors = validate_required_keys(doc)
    assert any(e.code == "MISSING_REQUIRED_KEY" for e in errors)

def test_missing_common_field():
    doc = minimal_valid_doc()
    doc["period"].pop("confidence")
    errors = validate_required_keys(doc)
    assert any(e.code == "MISSING_COMMON_FIELD" for e in errors)

def test_invalid_confidence():
    doc = minimal_valid_doc()
    doc["period"]["confidence"] = "unknown"
    errors = validate_required_keys(doc)
    assert any(e.code == "INVALID_CONFIDENCE" for e in errors)

def test_span_anchor_inconsistent():
    doc = minimal_valid_doc()
    doc["period"]["evidence_span"] = "지난달부터"
    doc["period"]["evidence_anchor"] = None
    errors = validate_required_keys(doc)
    assert any(e.code == "SPAN_ANCHOR_INCONSISTENT" for e in errors)