from uuid import uuid4

from ansimon_ai.timeline.types import TimelineDateItem, TimelineEvent, TimelineEvidenceItem
from ansimon_ai.writing.build_input import build_complaint_writing_input

def test_build_complaint_writing_input_preserves_manual_item_flag() -> None:
    complaint_id = uuid4()

    timeline_items = [
        TimelineDateItem(
            date="2026-02-18",
            events=[
                TimelineEvent(
                    time="17:00",
                    evidences=[
                        TimelineEvidenceItem(
                            timeline_evidence_id=uuid4(),
                            index=1,
                            title="퇴근길 접근 시도",
                            description="퇴근길 편의점 앞에서 피고소인이 직접 접근을 시도하였고, 고소인은 주변에 도움을 요청하였다.",
                            tags=["physical", "threat"],
                            is_ai_original=False,
                            referenced_evidence_ids=[],
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

    evidence = result.items[0].events[0].evidences[0]
    assert evidence.title == "퇴근길 접근 시도"
    assert evidence.is_ai_original is False
    assert evidence.referenced_evidence_ids == []