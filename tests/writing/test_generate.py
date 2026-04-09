import json
from uuid import uuid4

from ansimon_ai.llm.mock import MockLLMClient
from ansimon_ai.writing.generate import (
    generate_complaint_document,
    generate_damage_facts_statement,
)
from schemas.complaint_writing import (
    ComplaintWritingAiInput,
    ComplaintWritingDateItem,
    ComplaintWritingEvent,
    ComplaintWritingStructuredContext,
    ComplaintWritingTimelineItem,
)

class DummyLLMClient:
    def __init__(self, response: dict) -> None:
        self._response = response
        self.last_messages: list[dict] | None = None

    def generate(self, messages: list[dict]) -> str:
        self.last_messages = messages
        return json.dumps(self._response, ensure_ascii=False)

def _make_ai_input() -> ComplaintWritingAiInput:
    return ComplaintWritingAiInput(
        complaint_id=uuid4(),
        items=[
            ComplaintWritingDateItem(
                date="2026-02-12",
                events=[
                    ComplaintWritingEvent(
                        time="11:45",
                        evidences=[
                            ComplaintWritingTimelineItem(
                                title="피해 관련 사진",
                                description="스토킹 피해와 관련된 사진이다.",
                                tags=["physical"],
                                is_ai_original=True,
                                referenced_evidence_ids=[uuid4()],
                            )
                        ],
                    )
                ],
            )
        ],
        structured_contexts=[
            ComplaintWritingStructuredContext(
                evidence_id=uuid4(),
                channel=["offline"],
                locations=["주거지"],
                action_types=["접근", "폭행"],
                impact_on_victim=["불안", "공포"],
            )
        ],
    )

def test_generate_complaint_document_returns_valid_output() -> None:
    llm_client = DummyLLMClient(
        {
            "section_4_crime_facts": "범죄 사실 본문",
            "section_5_complaint_reason": "고소 이유 본문",
            "section_6_evidence_list_text": ["피해 관련 사진 (2026.02.12, 1건)"],
        }
    )

    result = generate_complaint_document(_make_ai_input(), llm_client=llm_client)

    assert result.section_4_crime_facts == "범죄 사실 본문"
    assert result.section_5_complaint_reason == "고소 이유 본문"
    assert result.section_6_evidence_list_text == [
        "피해 관련 사진 (2026.02.12, 1건)"
    ]
    assert llm_client.last_messages is not None

def test_generate_damage_facts_statement_returns_valid_output() -> None:
    llm_client = DummyLLMClient(
        {
            "damage_facts_statement": "피해 사실 진술 본문",
        }
    )

    result = generate_damage_facts_statement(_make_ai_input(), llm_client=llm_client)

    assert result.damage_facts_statement == "피해 사실 진술 본문"
    assert llm_client.last_messages is not None

def test_generate_document_outputs_with_mock_llm_client() -> None:
    ai_input = _make_ai_input()
    llm_client = MockLLMClient()

    complaint_result = generate_complaint_document(ai_input, llm_client=llm_client)
    statement_result = generate_damage_facts_statement(ai_input, llm_client=llm_client)

    assert complaint_result.section_4_crime_facts
    assert complaint_result.section_5_complaint_reason
    assert complaint_result.section_6_evidence_list_text
    assert statement_result.damage_facts_statement