from ansimon_ai.validator.runner import ValidatorRunner
from ansimon_ai.validator.rules.schema_exists import validate_schema_exists
from ansimon_ai.validator.rules.schema.required_keys import validate_required_top_level_keys

BASE = {
    "evidence_metadata": {},
    "parties": {},
    "period": {},
    "frequency": {},
    "channel": {},
    "locations": {},
    "action_types": {},
    "refusal_signal": {},
    "threat_indicators": {},
    "impact_on_victim": {},
    "report_or_record": {},
}

def test_required_keys_pass():
    runner = ValidatorRunner([validate_schema_exists, validate_required_top_level_keys])
    r = runner.run(BASE)
    assert r.status.value == "pass"

def test_required_keys_fail():
    bad = dict(BASE)
    bad.pop("period")
    runner = ValidatorRunner([validate_schema_exists, validate_required_top_level_keys])
    r = runner.run(bad)
    assert r.status.value == "fail"