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