from pathlib import Path
from uuid import uuid4

from ansimon_ai.llm.mock import MockLLMClient
from ansimon_ai.ocr.types import OCRResult, OCRSegment
from ansimon_ai.stt.mock import MockSTT
from ansimon_ai.timeline import (
    IncidentLogFormInput,
    TimelinePrototypeAiInput,
    TimelinePrototypeEvidenceInput,
    build_timeline_prototype,
)

TEST_TMP_DIR = Path("data/_timeline_test_tmp")

def _write_test_file(name: str, content: bytes) -> Path:
    TEST_TMP_DIR.mkdir(parents=True, exist_ok=True)
    path = TEST_TMP_DIR / name
    path.write_bytes(content)
    return path

def test_build_timeline_prototype_completes_incident_log_and_skips_victim():
    payload = TimelinePrototypeAiInput(
        complaint_id=uuid4(),
        evidences=[
            TimelinePrototypeEvidenceInput(
                evidence_id=uuid4(),
                type="INCIDENT_LOG",
                incident_log_form=IncidentLogFormInput(
                    title="incident title",
                    date="2026-03-19",
                    time="21:10",
                    place="home",
                    situation="the actor repeatedly knocked on the door",
                ),
            ),
            TimelinePrototypeEvidenceInput(
                evidence_id=uuid4(),
                type="VICTIM",
                file_format="IMAGE",
            ),
        ],
    )

    result = build_timeline_prototype(payload, llm_client=MockLLMClient())

    assert result.model_version == "prototype-v1"
    assert len(result.evidence_results) == 2

    completed = next(item for item in result.evidence_results if item.type == "INCIDENT_LOG")
    skipped = next(item for item in result.evidence_results if item.type == "VICTIM")

    assert completed.status == "completed"
    assert completed.source_type == "form"
    assert completed.title == "incident title"
    assert completed.structured_data is not None

    assert skipped.status == "skipped"
    assert skipped.error_code == "UNSUPPORTED_EVIDENCE_TYPE"

    assert len(result.items) == 1
    assert result.items[0].date == "2026-03-19"
    assert len(result.items[0].events) == 1
    assert result.items[0].events[0].evidences[0].title == "incident title"

def test_build_timeline_prototype_uses_extracted_text_for_report_record():
    payload = TimelinePrototypeAiInput(
        complaint_id=uuid4(),
        evidences=[
            TimelinePrototypeEvidenceInput(
                evidence_id=uuid4(),
                type="REPORT_RECORD",
                file_format="TXT",
                extracted_text="2026-03-18 상담 기록\n반복적으로 연락이 왔다.",
            ),
        ],
    )

    result = build_timeline_prototype(payload, llm_client=MockLLMClient())

    assert len(result.evidence_results) == 1
    evidence_result = result.evidence_results[0]

    assert evidence_result.status == "completed"
    assert evidence_result.source_type == "document"
    assert evidence_result.normalized_text is not None
    assert result.items[0].date == "2026-03-18"

def test_build_timeline_prototype_skips_hwp_report_record_without_extracted_text():
    payload = TimelinePrototypeAiInput(
        complaint_id=uuid4(),
        evidences=[
            TimelinePrototypeEvidenceInput(
                evidence_id=uuid4(),
                type="REPORT_RECORD",
                file_format="HWP",
                local_path="D:/fake/sample.hwp",
                file_name="sample.hwp",
            ),
        ],
    )

    result = build_timeline_prototype(payload, llm_client=MockLLMClient())

    evidence_result = result.evidence_results[0]
    assert evidence_result.status == "skipped"
    assert evidence_result.error_code == "UNSUPPORTED_FILE_FORMAT"
    assert evidence_result.error_message is not None
    assert "require extracted_text" in evidence_result.error_message
    assert result.items == []

def test_build_timeline_prototype_accepts_hwp_report_record_with_extracted_text():
    payload = TimelinePrototypeAiInput(
        complaint_id=uuid4(),
        evidences=[
            TimelinePrototypeEvidenceInput(
                evidence_id=uuid4(),
                type="REPORT_RECORD",
                file_format="HWP",
                extracted_text="2026-03-16 상담 내용\n문서에서 추출된 텍스트",
                file_name="sample.hwp",
            ),
        ],
    )

    result = build_timeline_prototype(payload, llm_client=MockLLMClient())

    evidence_result = result.evidence_results[0]
    assert evidence_result.status == "completed"
    assert evidence_result.source_type == "document"
    assert result.items[0].date == "2026-03-16"

def test_build_timeline_prototype_processes_message_image_with_injected_ocr():
    image_path = _write_test_file(f"{uuid4()}-message.png", b"fake-image")

    def fake_ocr_runner(_image_path: str) -> OCRResult:
        return OCRResult(
            full_text="2026-03-17 18:30 repeated threatening message",
            segments=[
                OCRSegment(
                    text="2026-03-17 18:30 repeated threatening message",
                )
            ],
            language="ko",
            engine="fake-ocr",
        )

    payload = TimelinePrototypeAiInput(
        complaint_id=uuid4(),
        evidences=[
            TimelinePrototypeEvidenceInput(
                evidence_id=uuid4(),
                type="MESSAGE",
                file_format="IMAGE",
                local_path=str(image_path),
                file_name="message.png",
            ),
        ],
    )

    result = build_timeline_prototype(
        payload,
        llm_client=MockLLMClient(),
        ocr_runner=fake_ocr_runner,
    )

    evidence_result = result.evidence_results[0]
    assert evidence_result.status == "completed"
    assert evidence_result.source_type == "ocr"
    assert evidence_result.normalized_text is not None
    assert result.items[0].date == "2026-03-17"

def test_build_timeline_prototype_processes_voice_audio_with_injected_stt():
    audio_path = _write_test_file(f"{uuid4()}-voice.m4a", b"fake-audio")

    payload = TimelinePrototypeAiInput(
        complaint_id=uuid4(),
        evidences=[
            TimelinePrototypeEvidenceInput(
                evidence_id=uuid4(),
                type="VOICE",
                file_format="AUDIO",
                local_path=str(audio_path),
                file_name="voice.m4a",
            ),
        ],
    )

    result = build_timeline_prototype(
        payload,
        llm_client=MockLLMClient(),
        stt_engine=MockSTT(),
    )

    evidence_result = result.evidence_results[0]
    assert evidence_result.status == "completed"
    assert evidence_result.source_type == "stt"
    assert evidence_result.normalized_text == str(audio_path)