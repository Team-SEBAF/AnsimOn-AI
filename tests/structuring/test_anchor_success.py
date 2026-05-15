import json
from uuid import uuid4

from ansimon_ai.structuring.anchor.matcher import AnchorMatcher
from ansimon_ai.structuring.run import run_structuring_pipeline
from ansimon_ai.structuring.types import StructuringInput, StructuringSegment
from tests.structuring._mocks import MemoryCache, MockValidator

class MockLLM:
    def generate(self, messages):
        return json.dumps(
            {
                "event": {
                    "value": "contact",
                    "confidence": "high",
                    "evidence_span": "called at 10pm",
                }
            },
            ensure_ascii=False,
        )

def _make_struct_input() -> StructuringInput:
    return StructuringInput(
        modality="text",
        source_type="stt",
        language="ko",
        full_text="They called at 10pm yesterday.",
        segments=[
            StructuringSegment(
                text="They called at 10pm yesterday.",
                start=0.0,
                end=3.0,
            )
        ],
    )

def test_anchor_success():
    result = run_structuring_pipeline(
        input=_make_struct_input(),
        llm_client=MockLLM(),
        anchor_matcher=AnchorMatcher(),
        validator=MockValidator(),
        cache=MemoryCache(),
    )

    assert result.anchor_stats.total_spans == 1
    assert result.anchor_stats.matched_spans == 1
    assert result.anchor_stats.unmatched_spans == 0

def test_cache_key_changes_with_evidence_id():
    cache = MemoryCache()

    first_result = run_structuring_pipeline(
        input=_make_struct_input(),
        llm_client=MockLLM(),
        anchor_matcher=AnchorMatcher(),
        validator=MockValidator(),
        evidence_id=uuid4(),
        cache=cache,
    )
    second_result = run_structuring_pipeline(
        input=_make_struct_input(),
        llm_client=MockLLM(),
        anchor_matcher=AnchorMatcher(),
        validator=MockValidator(),
        evidence_id=uuid4(),
        cache=cache,
    )

    assert first_result.run_id != second_result.run_id
    assert len(cache) == 2