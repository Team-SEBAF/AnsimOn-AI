from ansimon_ai.stt.mock import MockSTT
from ansimon_ai.structuring.from_stt import build_structuring_input_from_stt
from ansimon_ai.structuring.call import call_structuring_ai
from ansimon_ai.llm.mock import MockLLMClient

def test_call_structuring_ai_smoke():
    stt = MockSTT()
    stt_result = stt.transcribe("dummy.mp3")
    struct_input = build_structuring_input_from_stt(stt_result)

    llm = MockLLMClient()

    result = call_structuring_ai(struct_input, llm)

    assert isinstance(result, dict)

    expected_keys = {
        "evidence_metadata",
        "parties",
        "period",
        "frequency",
        "channel",
        "locations",
        "action_types",
        "refusal_signal",
        "threat_indicators",
        "impact_on_victim",
        "report_or_record",
    }

    assert set(result.keys()) == expected_keys