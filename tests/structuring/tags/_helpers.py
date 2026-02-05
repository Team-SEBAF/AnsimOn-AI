from ansimon_ai.structuring.types import (
    StructuringResult,
    AnchorStats,
    ValidationResult,
)

def make_result(
    *,
    matched: int,
    unmatched: int,
    output_json,
    validation_status: str = "PASS",
):
    return StructuringResult(
        output_json=output_json,
        cache_hit=False,
        anchor_stats=AnchorStats(
            total_spans=matched + unmatched,
            matched_spans=matched,
            partial_matched_spans=0,
            unmatched_spans=unmatched,
            notes=None,
        ),
        validation=ValidationResult(
            status=validation_status,
            error_codes=[],
            message=None,
        ),
        run_id="test",
    )