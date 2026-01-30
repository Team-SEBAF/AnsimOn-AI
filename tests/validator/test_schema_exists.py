from ansimon_ai.validator.runner import ValidatorRunner
from ansimon_ai.validator.rules.schema_exists import validate_schema_exists

def test_schema_exists_pass():
    runner = ValidatorRunner([validate_schema_exists])
    result = runner.run({"key": "value"})

    assert result.status.value == "pass"

def test_schema_exists_fail_when_not_dict():
    runner = ValidatorRunner([validate_schema_exists])
    result = runner.run("invalid")

    assert result.status.value == "fail"
