from ansimon_ai.stt.diarization import DiarizationSegment, assign_speakers_to_stt_segments
from ansimon_ai.stt.types import STTResult, STTSegment
from ansimon_ai.structuring.from_stt import build_structuring_input_from_stt

def test_assign_speakers_to_stt_segments_uses_largest_overlap() -> None:
    stt_result = STTResult(
        full_text="그만 연락하세요 신고해도 소용없어",
        segments=[
            STTSegment(start=0.0, end=2.0, text="그만 연락하세요"),
            STTSegment(start=2.0, end=5.0, text="신고해도 소용없어"),
        ],
        language="ko",
        engine="mock",
    )
    diarization_segments = [
        DiarizationSegment(start=0.0, end=2.2, speaker="SPEAKER_00"),
        DiarizationSegment(start=2.2, end=5.0, speaker="SPEAKER_01"),
    ]

    assigned = assign_speakers_to_stt_segments(stt_result, diarization_segments)

    assert assigned.segments[0].speaker == "SPEAKER_00"
    assert assigned.segments[1].speaker == "SPEAKER_01"

def test_build_structuring_input_from_stt_preserves_speaker_labels() -> None:
    stt_result = STTResult(
        full_text="그만 연락하세요 신고해도 소용없어",
        segments=[
            STTSegment(
                start=0.0,
                end=2.0,
                text="그만 연락하세요",
                speaker="SPEAKER_00",
            ),
            STTSegment(
                start=2.0,
                end=5.0,
                text="신고해도 소용없어",
                speaker="SPEAKER_01",
            ),
        ],
        language="ko",
        engine="mock",
    )

    struct_input = build_structuring_input_from_stt(stt_result)

    assert struct_input.segments[0].speaker == "SPEAKER_00"
    assert struct_input.segments[1].speaker == "SPEAKER_01"