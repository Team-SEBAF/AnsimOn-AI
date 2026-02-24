import os
import pytest
from ansimon_ai.stt import WhisperSTT
from ansimon_ai.structuring.tag_patterns import extract_tags_from_structuring_input

SAMPLE_AUDIO = os.environ.get("WHISPER_TEST_AUDIO", "D:/Project/AnsimOn/call_sample2.m4a")

@pytest.mark.skipif(not os.path.exists(SAMPLE_AUDIO), reason="샘플 오디오 파일이 존재하지 않음")
def test_whisper_stt_and_tag_extraction():
    stt = WhisperSTT()
    stt_result = stt.transcribe(SAMPLE_AUDIO)
    assert stt_result.full_text, "전체 텍스트가 비어 있지 않아야 함"
    assert stt_result.segments, "segment가 1개 이상 있어야 함"
    tags = extract_tags_from_structuring_input(stt_result)
    assert isinstance(tags, list)

    for seg in stt_result.segments:
        seg_result = stt_result.model_copy(update={"segments": [seg]})
        seg_tags = extract_tags_from_structuring_input(seg_result)
        assert isinstance(seg_tags, list)