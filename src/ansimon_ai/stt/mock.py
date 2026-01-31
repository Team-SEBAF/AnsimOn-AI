from .base import STTEngine
from .types import STTResult, STTSegment

class MockSTT(STTEngine):
    def transcribe(self, audio_path: str) -> STTResult:
        # NOTE: v0 단계에서는 실제 오디오 대신 "텍스트"를 넘겨 데모를 돌릴 수 있게
        # 입력 문자열을 그대로 full_text로 사용합니다.
        text = (audio_path or "").strip()
        if text:
            segments = [
                STTSegment(start=0.0, end=0.0, text=text),
            ]
            full_text = text
        else:
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
