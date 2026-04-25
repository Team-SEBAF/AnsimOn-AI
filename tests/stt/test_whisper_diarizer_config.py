import pytest

import ansimon_ai.stt.whisper_stt as whisper_stt_module

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

def test_resolve_diarizer_rejects_unsupported_engine(monkeypatch) -> None:
    monkeypatch.setenv("DIARIZATION_ENGINE", "unknown")

    with pytest.raises(ValueError, match="Unsupported diarization engine"):
        whisper_stt_module._resolve_diarizer()