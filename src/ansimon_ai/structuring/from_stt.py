from ansimon_ai.stt.types import STTResult
from .types import StructuringInput, StructuringSegment

def build_structuring_input_from_stt(stt: STTResult) -> StructuringInput:
    return StructuringInput(
        modality="text",
        source_type="stt",
        language=stt.language,
        full_text=stt.full_text,
        segments=[
            StructuringSegment(
                text=seg.text,
                start=seg.start,
                end=seg.end,
            )
            for seg in stt.segments
        ],
    )