from datetime import datetime

from ansimon_ai.structuring.cache.hash import compute_input_hash
from ansimon_ai.structuring.types import StructuringInput, StructuringSegment


def test_compute_input_hash_accepts_datetime_timestamps() -> None:
    struct_input = StructuringInput(
        modality="text",
        source_type="document",
        language="ko",
        full_text="2026-03-19 repeated threatening messages were documented.",
        segments=[
            StructuringSegment(
                text="2026-03-19 repeated threatening messages were documented.",
                start=0.0,
                end=1.0,
                timestamp=datetime(2026, 3, 19, 8, 45),
            )
        ],
    )

    result = compute_input_hash(
        struct_input,
        schema_version="v1.5",
        prompt_version="v1.2",
    )

    assert isinstance(result, str)
    assert result