import json
from pathlib import Path
import pytest

from ansimon_ai.structuring.cache.manager import get_or_create_structured_result
from ansimon_ai.structuring.types import StructuringInput

def _make_input(text: str) -> StructuringInput:
    return StructuringInput(
        modality="text",
        source_type="stt",
        language="ko",
        full_text=text,
        segments=[],
    )

def test_cache_miss_creates_and_saves(tmp_path: Path):
    call_count = {"n": 0}

    def fake_call(_):
        call_count["n"] += 1
        return {"ok": True}

    def path_fn(schema_version: str, input_hash: str) -> Path:
        return tmp_path / schema_version / f"{input_hash}.json"

    result = get_or_create_structured_result(
        _make_input("hello"),
        fake_call,
        schema_version="v1.3",
        prompt_version="system_prompt_v0",
        storage_path_fn=path_fn,
    )

    assert call_count["n"] == 1
    assert "result" in result
    assert result["result"] == {"ok": True}
    assert (tmp_path / "v1.3").exists()

def test_cache_hit_skips_call(tmp_path: Path):
    call_count = {"n": 0}

    def fake_call(_):
        call_count["n"] += 1
        return {"ok": True}

    def path_fn(schema_version: str, input_hash: str) -> Path:
        return tmp_path / schema_version / f"{input_hash}.json"

    get_or_create_structured_result(
        _make_input("same input"),
        fake_call,
        storage_path_fn=path_fn,
    )

    result = get_or_create_structured_result(
        _make_input("same input"),
        fake_call,
        storage_path_fn=path_fn,
    )

    assert call_count["n"] == 1
    assert result["result"] == {"ok": True}

def test_prompt_version_change_causes_cache_miss(tmp_path: Path):
    call_count = {"n": 0}

    def fake_call(_):
        call_count["n"] += 1
        return {"ok": True}

    def path_fn(schema_version: str, input_hash: str) -> Path:
        return tmp_path / schema_version / f"{input_hash}.json"

    get_or_create_structured_result(
        _make_input("hello"),
        fake_call,
        prompt_version="system_prompt_v0",
        storage_path_fn=path_fn,
    )

    get_or_create_structured_result(
        _make_input("hello"),
        fake_call,
        prompt_version="system_prompt_v1",
        storage_path_fn=path_fn,
    )

    assert call_count["n"] == 2

def test_broken_cache_file_raises_and_allows_regeneration(tmp_path: Path):
    call_count = {"n": 0}

    def fake_call(_):
        call_count["n"] += 1
        return {"ok": True}

    def path_fn(schema_version: str, input_hash: str) -> Path:
        return tmp_path / schema_version / f"{input_hash}.json"

    get_or_create_structured_result(
        _make_input("hello"),
        fake_call,
        storage_path_fn=path_fn,
    )

    files = list((tmp_path / "v1.3").glob("*.json"))
    assert len(files) == 1

    with files[0].open("w", encoding="utf-8") as f:
        f.write("{ invalid json")

    with pytest.raises(json.JSONDecodeError):
        get_or_create_structured_result(
            _make_input("hello"),
            fake_call,
            storage_path_fn=path_fn,
        )