from ansimon_ai.stt.mock import MockSTT
from ansimon_ai.structuring.from_stt import build_structuring_input_from_stt

def test_build_structuring_input_from_stt():
    stt = MockSTT()
    stt_result = stt.transcribe("dummy.mp3")

    struct_input = build_structuring_input_from_stt(stt_result)

    assert struct_input.modality == "text"
    assert struct_input.source_type == "stt"
    assert struct_input.full_text == stt_result.full_text
    assert len(struct_input.segments) == len(stt_result.segments)