import pytest

import ansimon_ai.stt.whisper_stt as whisper_stt_module
from ansimon_ai.stt.whisper_stt import WhisperSTT

def test_resolve_diarizer_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("DIARIZATION_ENGINE", raising=False)

    assert whisper_stt_module._resolve_diarizer() is None

def test_resolve_diarizer_supports_off_values(monkeypatch) -> None:
    for value in ("none", "off", "false"):
        monkeypatch.setenv("DIARIZATION_ENGINE", value)

        assert whisper_stt_module._resolve_diarizer() is None

def test_resolve_diarizer_builds_pyannote_diarizer(monkeypatch) -> None:
    class FakeDiarizer:
        pass

    monkeypatch.setenv("DIARIZATION_ENGINE", "pyannote")
    monkeypatch.setattr(whisper_stt_module, "PyannoteDiarizer", FakeDiarizer)

    assert isinstance(whisper_stt_module._resolve_diarizer(), FakeDiarizer)

def test_resolve_diarizer_returns_none_when_pyannote_initialization_fails(monkeypatch) -> None:
    class BrokenDiarizer:
        def __init__(self):
            raise OSError("torchaudio native library failed")

    monkeypatch.setenv("DIARIZATION_ENGINE", "pyannote")
    monkeypatch.setattr(whisper_stt_module, "PyannoteDiarizer", BrokenDiarizer)

    with pytest.warns(RuntimeWarning, match="Pyannote diarization is disabled"):
        assert whisper_stt_module._resolve_diarizer() is None

def test_resolve_diarizer_rejects_unsupported_engine(monkeypatch) -> None:
    monkeypatch.setenv("DIARIZATION_ENGINE", "unknown")

    with pytest.raises(ValueError, match="Unsupported diarization engine"):
        whisper_stt_module._resolve_diarizer()

def test_whisper_stt_returns_plain_result_when_diarization_fails(monkeypatch) -> None:
    class FakeModel:
        def transcribe(self, audio_path, language=None):
            return {
                "text": "통화 내용",
                "language": "ko",
                "segments": [
                    {
                        "start": 0.0,
                        "end": 1.0,
                        "text": "통화 내용",
                    }
                ],
            }

    class BrokenDiarizer:
        def diarize(self, audio_path):
            raise OSError("torchaudio native library failed")

    monkeypatch.setattr(whisper_stt_module.whisper, "load_model", lambda model_size: FakeModel())

    stt = WhisperSTT(diarizer=BrokenDiarizer())

    with pytest.warns(RuntimeWarning, match="Diarization failed"):
        result = stt.transcribe("sample.wav")

    assert result.full_text == "통화 내용"
    assert result.segments[0].speaker is None