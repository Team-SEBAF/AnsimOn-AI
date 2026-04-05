from pathlib import Path
import subprocess

import pytest

from ansimon_ai.video import extract_frames_from_video, get_video_duration_seconds

def test_extract_frames_from_video_runs_ffmpeg_and_returns_frame_metadata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    video_path = tmp_path / "sample.mp4"
    video_path.write_bytes(b"fake-video")
    output_dir = tmp_path / "frames"

    recorded: dict[str, object] = {}

    def fake_run(command, check, capture_output, text):
        recorded["command"] = command
        recorded["check"] = check
        recorded["capture_output"] = capture_output
        recorded["text"] = text
        output_dir.mkdir(parents=True, exist_ok=True)
        for index in range(1, 4):
            (output_dir / f"frame_{index:06d}.jpg").write_bytes(b"jpg")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("ansimon_ai.video.extract_frames.subprocess.run", fake_run)

    frames = extract_frames_from_video(
        video_path,
        output_dir=output_dir,
        interval_seconds=10,
    )

    assert recorded["command"] == [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video_path),
        "-vf",
        "fps=1/10",
        str(output_dir / "frame_%06d.jpg"),
    ]
    assert recorded["check"] is True
    assert recorded["capture_output"] is True
    assert recorded["text"] is True

    assert [frame.frame_index for frame in frames] == [0, 1, 2]
    assert [frame.frame_timestamp_seconds for frame in frames] == [0, 10, 20]
    assert all(frame.path.exists() for frame in frames)

def test_extract_frames_from_video_rejects_invalid_interval(tmp_path: Path):
    video_path = tmp_path / "sample.mp4"
    video_path.write_bytes(b"fake-video")

    with pytest.raises(ValueError, match="interval_seconds"):
        extract_frames_from_video(
            video_path,
            output_dir=tmp_path / "frames",
            interval_seconds=0,
        )

def test_extract_frames_from_video_raises_when_no_frames_are_created(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    video_path = tmp_path / "sample.mp4"
    video_path.write_bytes(b"fake-video")

    def fake_run(command, check, capture_output, text):
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("ansimon_ai.video.extract_frames.subprocess.run", fake_run)

    with pytest.raises(ValueError, match="No frames"):
        extract_frames_from_video(
            video_path,
            output_dir=tmp_path / "frames",
            interval_seconds=5,
        )

def test_get_video_duration_seconds_parses_ffprobe_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    video_path = tmp_path / "sample.mp4"
    video_path.write_bytes(b"fake-video")

    recorded: dict[str, object] = {}

    def fake_run(command, check, capture_output, text):
        recorded["command"] = command
        recorded["check"] = check
        recorded["capture_output"] = capture_output
        recorded["text"] = text
        return subprocess.CompletedProcess(
            command,
            0,
            '{"format":{"duration":"12.345"}}',
            "",
        )

    monkeypatch.setattr("ansimon_ai.video.extract_frames.subprocess.run", fake_run)

    duration = get_video_duration_seconds(video_path)

    assert recorded["command"] == [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(video_path),
    ]
    assert recorded["check"] is True
    assert recorded["capture_output"] is True
    assert recorded["text"] is True
    assert duration == 12.345