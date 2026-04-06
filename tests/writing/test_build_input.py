from uuid import uuid4

from ansimon_ai.timeline.types import (
    EvidenceProcessingResult,
    TimelineDateItem,
    TimelineEvent,
    TimelineEvidenceItem,
)
from ansimon_ai.writing.build_input import build_complaint_writing_input

def test_build_complaint_writing_input_maps_timeline_items() -> None:
    evidence_id = uuid4()
    complaint_id = uuid4()

    timeline_items = [
        TimelineDateItem(
            date="2026-02-12",
            events=[
                TimelineEvent(
                    time="11:45",
                    evidences=[
                        TimelineEvidenceItem(
                            timeline_evidence_id=uuid4(),
                            index=1,
                            title="피해 관련 사진",
                            description="스토킹 피해 관련 사진이다.",
                            tags=["physical"],
                            referenced_evidence_ids=[evidence_id],
                        )
                    ],
                )
            ],
        )
    ]

    result = build_complaint_writing_input(
        complaint_id=complaint_id,
        timeline_items=timeline_items,
        evidence_results=[],
    )

    assert result.complaint_id == complaint_id
    assert result.items[0].date == "2026-02-12"
    assert result.items[0].events[0].time == "11:45"
    assert result.items[0].events[0].evidences[0].title == "피해 관련 사진"
    assert result.items[0].events[0].evidences[0].is_ai_original is True
    assert result.items[0].events[0].evidences[0].referenced_evidence_ids == [
        evidence_id
    ]

def test_build_complaint_writing_input_filters_structured_contexts() -> None:
    referenced_evidence_id = uuid4()
    unreferenced_evidence_id = uuid4()

    timeline_items = [
        TimelineDateItem(
            date="2026-02-12",
            events=[
                TimelineEvent(
                    time="11:45",
                    evidences=[
                        TimelineEvidenceItem(
                            timeline_evidence_id=uuid4(),
                            index=1,
                            title="피해 관련 사진",
                            description="스토킹 피해 관련 사진이다.",
                            tags=["physical"],
                            referenced_evidence_ids=[referenced_evidence_id],
                        )
                    ],
                )
            ],
        )
    ]

    evidence_results = [
        EvidenceProcessingResult(
            evidence_id=referenced_evidence_id,
            type="VICTIM",
            status="completed",
            structured_data={
                "parties": {
                    "value": {
                        "actor": "가해자",
                        "target": "피해자",
                        "relationship": "전 연인",
                    }
                },
                "period": {"value": "2026-02-12"},
                "frequency": {"value": "unknown"},
                "channel": {"value": ["offline"]},
                "locations": {"value": ["주차장"]},
                "action_types": {"value": ["접근", "폭행"]},
                "refusal_signal": {"value": "unknown"},
                "threat_indicators": {"value": ["신체적 위해"]},
                "impact_on_victim": {"value": ["불안", "공포"]},
                "report_or_record": {"value": "unknown"},
            },
        ),
        EvidenceProcessingResult(
            evidence_id=unreferenced_evidence_id,
            type="MESSAGE",
            status="completed",
            structured_data={
                "parties": {"value": {"actor": "가해자", "target": "피해자"}},
                "channel": {"value": ["kakao"]},
            },
        ),
    ]

    result = build_complaint_writing_input(
        complaint_id=uuid4(),
        timeline_items=timeline_items,
        evidence_results=evidence_results,
    )

    assert len(result.structured_contexts) == 1

    context = result.structured_contexts[0]
    assert context.evidence_id == referenced_evidence_id
    assert context.parties == {
        "actor": "가해자",
        "target": "피해자",
        "relationship": "전 연인",
    }
    assert context.period == "2026-02-12"
    assert context.frequency is None
    assert context.channel == ["offline"]
    assert context.locations == ["주차장"]
    assert context.action_types == ["접근", "폭행"]
    assert context.refusal_signal is None
    assert context.threat_indicators == ["신체적 위해"]
    assert context.impact_on_victim == ["불안", "공포"]
    assert context.report_or_record is None