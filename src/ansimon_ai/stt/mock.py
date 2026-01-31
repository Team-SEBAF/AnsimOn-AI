from .base import STTEngine
from .types import STTResult, STTSegment

class MockSTT(STTEngine):
    def transcribe(self, audio_path: str) -> STTResult:
        segments = [
            STTSegment(start=0.0, end=2.5, text="지금 어디야"),
            STTSegment(start=3.0, end=6.2, text="안 받으면 찾아갈 거야"),
        ]

        full_text = " ".join(seg.text for seg in segments)

        return STTResult(
            full_text=full_text,
            segments=segments,
            language="ko",
            engine="mock",
        )
