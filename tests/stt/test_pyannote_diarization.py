import io
from types import SimpleNamespace
import wave
import pytest

from ansimon_ai.stt.pyannote_diarization import PyannoteDiarizer, _load_wav_bytes

class FakeDiarization:
    def itertracks(self, yield_label=False):
        assert yield_label is True
        yield SimpleNamespace(start=0.0, end=2.0), None, "SPEAKER_00"
        yield SimpleNamespace(start=2.0, end=5.0), None, "SPEAKER_01"

class FakePyannote4Pipeline:
    def __call__(self, audio_input, *, min_speakers=None, max_speakers=None):
        return SimpleNamespace(
            speaker_diarization=FakeDiarization(),
            exclusive_speaker_diarization=FakeDiarization(),
        )

class FakePipeline:
    def __init__(self):
        self.calls = []

    def __call__(self, audio_input, *, min_speakers=None, max_speakers=None):
        self.calls.append(
            {
                "audio_input": audio_input,
                "min_speakers": min_speakers,
                "max_speakers": max_speakers,
            }
        )
        return FakeDiarization()

def test_pyannote_diarizer_requires_token(monkeypatch) -> None:
    monkeypatch.delenv("PYANNOTE_HF_TOKEN", raising=False)

    with pytest.raises(ValueError, match="PYANNOTE_HF_TOKEN"):
        PyannoteDiarizer(pipeline_factory=lambda _model, _token: FakePipeline())

def test_pyannote_diarizer_parses_pipeline_output() -> None:
    pipeline = FakePipeline()

    diarizer = PyannoteDiarizer(
        token="token",
        model="model",
        min_speakers=1,
        max_speakers=3,
        pipeline_factory=lambda model, token: pipeline,
        audio_loader=lambda audio_path: {
            "waveform": "fake-waveform",
            "sample_rate": 16000,
        },
    )

    segments = diarizer.diarize("sample.wav")

    assert pipeline.calls == [
        {
            "audio_input": {
                "waveform": "fake-waveform",
                "sample_rate": 16000,
            },
            "min_speakers": 1,
            "max_speakers": 3,
        }
    ]
    assert [segment.speaker for segment in segments] == ["SPEAKER_00", "SPEAKER_01"]
    assert segments[0].start == 0.0
    assert segments[1].end == 5.0

def test_pyannote_diarizer_parses_pyannote4_output() -> None:
    diarizer = PyannoteDiarizer(
        token="token",
        pipeline_factory=lambda model, token: FakePyannote4Pipeline(),
        audio_loader=lambda audio_path: audio_path,
    )

    segments = diarizer.diarize("sample.wav")

    assert [segment.speaker for segment in segments] == ["SPEAKER_00", "SPEAKER_01"]

def test_pyannote_diarizer_falls_back_to_audio_path_when_loader_fails() -> None:
    pipeline = FakePipeline()

    diarizer = PyannoteDiarizer(
        token="token",
        pipeline_factory=lambda model, token: pipeline,
        audio_loader=lambda audio_path: (_ for _ in ()).throw(RuntimeError("load failed")),
    )

    diarizer.diarize("sample.m4a")

    assert pipeline.calls[0]["audio_input"] == "sample.m4a"
    assert pipeline.calls[0]["min_speakers"] == 2
    assert pipeline.calls[0]["max_speakers"] == 2

def test_load_wav_bytes_returns_pyannote_audio_input() -> None:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes((0).to_bytes(2, byteorder="little", signed=True) * 160)

    audio_input = _load_wav_bytes(buffer.getvalue())

    assert audio_input["sample_rate"] == 16000
    assert audio_input["waveform"].shape == (1, 160)