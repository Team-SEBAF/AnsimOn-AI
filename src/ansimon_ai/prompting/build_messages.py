import base64
import json
from pathlib import Path

from ansimon_ai.structuring.types import StructuringInput

PROMPT_PATH = Path(__file__).parent / "system_prompt_v0.txt"

def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

def build_structuring_messages(struct_input: StructuringInput) -> list[dict]:
    segments_json = json.dumps(
        [seg.model_dump(mode="json") for seg in struct_input.segments],
        ensure_ascii=False,
        indent=2,
    )

    return [
        {
            "role": "system",
            "content": load_system_prompt(),
        },
        {
            "role": "user",
            "content": (
                "### INPUT TEXT (anchor base)\n\n"
                f"{struct_input.full_text}\n\n"
                "### SEGMENTS (json)\n\n"
                f"{segments_json}"
            ),
        },
    ]

def build_victim_image_messages(
    *,
    image_bytes: bytes,
    file_name: str | None = None,
    file_format: str | None = None,
) -> list[dict]:
    mime_type = _infer_image_mime_type(file_name=file_name, file_format=file_format)
    data_url = _build_image_data_url(image_bytes=image_bytes, mime_type=mime_type)

    context_lines = [
        "Analyze this victim evidence image and return a JSON object that follows the required schema.",
        "Focus only on what is visually observable in the image.",
        "Do not make medical, legal, or factual conclusions beyond the image itself.",
        "If something is unclear, use cautious language and lower confidence.",
        "If the image suggests bruising, injury, physical force, or sexual misconduct, describe it as an observation only.",
        "If visible date or time text appears in the image, use it when relevant.",
        "Because this is an image-first input, evidence_span and evidence_anchor may be null when no reliable text span exists.",
        "Assign the `physical` tag only when bodily injury marks, bruising, bleeding, restraint, or strong physical force are comparatively clear in the image.",
        "Do not assign the `physical` tag for simple touch or ambiguous contact alone.",
        "Assign the `sexual_insult` tag only when sexual exposure, sexual humiliation, or unwanted sexual contact is comparatively clear in the image.",
        "Do not assign the `sexual_insult` tag when the sexual context is unclear or inferred only from pose or proximity.",
    ]
    if file_name:
        context_lines.append(f"File name: {file_name}")

    return [
        {
            "role": "system",
            "content": load_system_prompt(),
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "\n".join(context_lines),
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_url,
                    },
                },
            ],
        },
    ]

def _infer_image_mime_type(*, file_name: str | None, file_format: str | None) -> str:
    if file_name:
        suffix = Path(file_name).suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            return "image/jpeg"
        if suffix == ".png":
            return "image/png"
        if suffix == ".webp":
            return "image/webp"
        if suffix == ".gif":
            return "image/gif"

    if file_format == "IMAGE":
        return "image/jpeg"

    return "application/octet-stream"

def _build_image_data_url(*, image_bytes: bytes, mime_type: str) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"