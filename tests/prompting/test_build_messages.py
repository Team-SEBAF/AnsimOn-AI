from ansimon_ai.stt.mock import MockSTT
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