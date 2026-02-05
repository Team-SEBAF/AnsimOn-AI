import json

from ansimon_ai.structuring.run import run_structuring_pipeline
from ansimon_ai.structuring.types import StructuringInput, StructuringSegment
from ansimon_ai.structuring.anchor.matcher import AnchorMatcher
from tests.structuring._mocks import MockValidator, MemoryCache

class MockLLM:
    def generate(self, messages):
        return json.dumps(
            {
                "event": {
                    "value": "contact",
                    "confidence": "high",
                    "evidence_span": "새벽 3시에 전화했다",
                }
            },
            ensure_ascii=False,
        )

def test_anchor_unmatched():
    struct_input = StructuringInput(
        modality="text",
        source_type="stt",
        language="ko",
        full_text="어제 밤 10시에 연락했다.",
        segments=[
            StructuringSegment(
                text="어제 밤 10시에 연락했다.",
                start=0.0,
                end=3.0,
            )
        ],
    )

    result = run_structuring_pipeline(
        input=struct_input,
        llm_client=MockLLM(),
        anchor_matcher=AnchorMatcher(),
        validator=MockValidator(),
        cache=MemoryCache(),
    )

    assert result.anchor_stats.total_spans == 1
    assert result.anchor_stats.matched_spans == 0
    assert result.anchor_stats.unmatched_spans == 1