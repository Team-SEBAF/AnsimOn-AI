from typing import Callable, List

from ansimon_ai.validator.result import (
    ValidationResult,
    ValidationStatus,
    ValidationMessage,
)

ValidatorFn = Callable[[dict], ValidationMessage | None]

class ValidatorRunner:
    def __init__(self, validators: List[ValidatorFn] | None = None):
        self.validators: List[ValidatorFn] = validators or []

    def add(self, validator: ValidatorFn) -> None:
        self.validators.append(validator)

    def run(self, data: dict) -> ValidationResult:
        messages: List[ValidationMessage] = []

        for validator in self.validators:
            msg = validator(data)
            if msg:
                messages.append(msg)

        status = self._decide_status(messages)

        return ValidationResult(
            status=status,
            messages=messages,
        )

    @staticmethod
    def _decide_status(messages: List[ValidationMessage]) -> ValidationStatus:
        if not messages:
            return ValidationStatus.PASS

        if any(m.code.startswith("E_") for m in messages):
            return ValidationStatus.FAIL

        return ValidationStatus.WARN