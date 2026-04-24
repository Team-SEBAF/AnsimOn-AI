from .base import STTEngine
from .diarization import assign_speakers_to_stt_segments
from .types import STTResult, STTSegment
import whisper

class WhisperSTT(STTEngine):
    def __init__(self, model_size: str = "base", diarizer=None):
        self.model = whisper.load_model(model_size)
        self.engine_name = f"whisper-{model_size}"
        self.diarizer = diarizer

    def transcribe(self, audio_path: str) -> STTResult:
        result = self.model.transcribe(audio_path, language="ko")
        segments = [
            STTSegment(
                start=seg["start"],
                end=seg["end"],
                text=seg["text"]
            )
            for seg in result["segments"]
        ]
        stt_result = STTResult(
            full_text=result["text"],
            segments=segments,
            language=result.get("language", "ko"),
            engine=self.engine_name
        )
        if self.diarizer is None:
            return stt_result

        diarization_segments = self.diarizer.diarize(audio_path)
        return assign_speakers_to_stt_segments(stt_result, diarization_segments)