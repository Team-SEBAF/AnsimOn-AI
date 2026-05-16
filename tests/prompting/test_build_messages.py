from ansimon_ai.stt.mock import MockSTT
from ansimon_ai.stt.types import STTResult, STTSegment
from ansimon_ai.structuring.from_stt import build_structuring_input_from_stt
from ansimon_ai.prompting.build_messages import build_structuring_messages, load_system_prompt

def test_build_structuring_messages_smoke():
    stt = MockSTT()
    stt_result = stt.transcribe("dummy.mp3")
    struct_input = build_structuring_input_from_stt(stt_result)

    system_prompt = load_system_prompt()
    messages = build_structuring_messages(struct_input)

    assert isinstance(system_prompt, str)
    assert len(system_prompt) > 0

    assert isinstance(messages, list)
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    assert struct_input.full_text in messages[1]["content"]
    assert "SEGMENTS" in messages[1]["content"]

def test_build_structuring_messages_includes_speaker_labeled_transcript_for_stt():
    stt_result = STTResult(
        full_text="전화를 건 쪽이 물었다. 상대가 거절했다.",
        segments=[
            STTSegment(start=0.0, end=2.0, text="왜 불편한지 모르겠어요.", speaker="SPEAKER_01"),
            STTSegment(start=2.0, end=4.0, text="네가 그냥 싫다고.", speaker="SPEAKER_00"),
            STTSegment(start=4.0, end=6.0, text="다시 연락할게요.", speaker="SPEAKER_01"),
        ],
        language="ko",
        engine="whisper-base",
    )
    struct_input = build_structuring_input_from_stt(stt_result)

    messages = build_structuring_messages(struct_input)
    user_content = messages[1]["content"]

    assert "SPEAKER ATTRIBUTION NOTE" in user_content
    assert "SPEAKER_01: 왜 불편한지 모르겠어요." in user_content
    assert "SPEAKER_01: 다시 연락할게요." in user_content
    assert "SPEAKER-LABELED TRANSCRIPT" in user_content

def test_build_structuring_messages_adds_speaker_role_consistency_note_for_stt():
    stt_result = STTResult(
        full_text=(
            "카톡이 계속 와서 부담스럽다. "
            "연락 안 하는 거다. "
            "선배로서 신입생을 챙긴 거다."
        ),
        segments=[
            STTSegment(
                start=0.0,
                end=2.0,
                text="카톡이 계속 와서 부담스럽다.",
                speaker="SPEAKER_00",
            ),
            STTSegment(
                start=2.0,
                end=4.0,
                text="연락 안 하는 거다.",
                speaker="SPEAKER_00",
            ),
            STTSegment(
                start=4.0,
                end=6.0,
                text="왜 이유를 모르겠냐.",
                speaker="SPEAKER_01",
            ),
            STTSegment(
                start=6.0,
                end=8.0,
                text="선배로서 신입생을 챙긴 거다.",
                speaker="SPEAKER_00",
            ),
        ],
        language="ko",
        engine="whisper-base",
    )
    struct_input = build_structuring_input_from_stt(stt_result)

    messages = build_structuring_messages(struct_input)
    user_content = messages[1]["content"]

    assert "SPEAKER ROLE CONSISTENCY NOTE" in user_content
    assert "Do not combine a refusal from one speaker" in user_content
    assert "Avoid using relationship labels" in user_content
    assert "`선배`" in user_content
    assert "`신입생`" in user_content

def test_build_structuring_messages_adds_defensive_response_guardrail_for_stt():
    stt_result = STTResult(
        full_text=(
            "차단된 것 같아서 다른 번호로 전화했어. "
            "주변에서 보고 있었어. 바로 신고한다."
        ),
        segments=[
            STTSegment(
                start=0.0,
                end=2.0,
                text="차단된 것 같아서 다른 번호로 전화했어.",
                speaker="SPEAKER_01",
            ),
            STTSegment(
                start=2.0,
                end=4.0,
                text="주변에서 보고 있었어.",
                speaker="SPEAKER_01",
            ),
            STTSegment(
                start=4.0,
                end=6.0,
                text="바로 신고한다.",
                speaker="SPEAKER_00",
            ),
        ],
        language="ko",
        engine="whisper-base",
    )
    struct_input = build_structuring_input_from_stt(stt_result)

    messages = build_structuring_messages(struct_input)
    user_content = messages[1]["content"]

    assert "contact or block-bypass context" in user_content
    assert "possible defensive reporting/legal-response language" in user_content
    assert "`신고한다`" in user_content
    assert "`끝까지 간다`" in user_content
    assert "`고소한다`" in user_content

def test_build_structuring_messages_discourages_direct_quotes_for_stt():
    stt_result = STTResult(
        full_text="이사까지 가면 죽여버린다. 날 환하게 하지 마.",
        segments=[
            STTSegment(
                start=0.0,
                end=2.0,
                text="이사까지 가면 죽여버린다.",
                speaker="SPEAKER_01",
            ),
            STTSegment(
                start=2.0,
                end=4.0,
                text="날 환하게 하지 마.",
                speaker="SPEAKER_01",
            ),
        ],
        language="ko",
        engine="whisper-base",
    )
    struct_input = build_structuring_input_from_stt(stt_result)

    messages = build_structuring_messages(struct_input)
    user_content = messages[1]["content"]

    assert "STT text can contain misrecognitions" in user_content
    assert "avoid direct quotation" in user_content
    assert "`취지의 발언`" in user_content

def test_build_structuring_messages_adds_single_speaker_voice_note():
    stt_result = STTResult(
        full_text="선배를 카페 앞에서 봤어요. 저 진짜 죽고 싶어요.",
        segments=[
            STTSegment(
                start=0.0,
                end=3.0,
                text="선배를 카페 앞에서 봤어요.",
                speaker="SPEAKER_00",
            ),
            STTSegment(
                start=3.0,
                end=6.0,
                text="저 진짜 죽고 싶어요.",
                speaker="SPEAKER_00",
            ),
        ],
        language="ko",
        engine="whisper-base",
    )
    struct_input = build_structuring_input_from_stt(stt_result)

    messages = build_structuring_messages(struct_input)
    user_content = messages[1]["content"]

    assert "one detected speaker only" in user_content
    assert "refer to this speaker as `상대방`" in user_content
    assert "`말한 사람`" in user_content