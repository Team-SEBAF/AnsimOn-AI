import base64
import json
from pathlib import Path

from schemas.complaint_writing import ComplaintWritingAiInput
from ansimon_ai.structuring.types import StructuringInput
from ansimon_ai.video import ExtractedVideoFrame

PROMPT_PATH = Path(__file__).parent / "system_prompt_v0.txt"
COMPLAINT_DOCUMENT_PROMPT_PATH = (
    Path(__file__).parent / "complaint_document_system_prompt_v0.txt"
)
DAMAGE_FACTS_STATEMENT_PROMPT_PATH = (
    Path(__file__).parent / "damage_facts_statement_system_prompt_v0.txt"
)

def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

def load_complaint_document_system_prompt() -> str:
    return COMPLAINT_DOCUMENT_PROMPT_PATH.read_text(encoding="utf-8")

def load_damage_facts_statement_system_prompt() -> str:
    return DAMAGE_FACTS_STATEMENT_PROMPT_PATH.read_text(encoding="utf-8")

def build_structuring_messages(struct_input: StructuringInput) -> list[dict]:
    segments_json = json.dumps(
        [seg.model_dump(mode="json") for seg in struct_input.segments],
        ensure_ascii=False,
        indent=2,
    )
    stt_section = _build_stt_context_section(struct_input)

    return [
        {
            "role": "system",
            "content": load_system_prompt(),
        },
        {
            "role": "user",
            "content": (
                f"{stt_section}"
                "### INPUT TEXT (anchor base)\n\n"
                f"{struct_input.full_text}\n\n"
                "### SEGMENTS (json)\n\n"
                f"{segments_json}"
            ),
        },
    ]

def _build_stt_context_section(struct_input: StructuringInput) -> str:
    if struct_input.source_type != "stt":
        return ""

    interpretation_note = (
        "### STT INTERPRETATION NOTE\n\n"
        "For call or conversation evidence, summarize the flow of contact, pressure, "
        "response, warning, and counter-response rather than mechanically replaying "
        "each line of dialogue. When the speaking subject is unclear, prefer omitting "
        "the subject in the final Korean title/description instead of repeatedly using "
        "`한쪽` or `다른 쪽`. Keep repeated contact, pressure, refusal, warning, and "
        "response in the original order. Do not decide that a speaker is the aggressor "
        "or that an utterance is threatening only because swear words appear; interpret "
        "swear words together with the surrounding contact, pressure, refusal, warning, "
        "and response flow. If a speaker says they called from another number because "
        "they were blocked, or if the conversation starts with a question about an "
        "unknown number or number source, treat that as contact or block-bypass context "
        "before interpreting later swear words or reporting warnings. Later statements "
        "such as `I'll report this`, `I'll go to the end`, `I'll sue`, or similar "
        "legal/reporting warnings may be defensive responses to prior contact, pressure, "
        "or monitoring; do not use those response lines alone as threat evidence or as "
        "the center of the Korean title/description. Korean response phrases such as "
        "`신고한다`, `끝까지 간다`, or `고소한다` should be treated as possible "
        "defensive reporting/legal-response language when they follow block-bypass, "
        "contact, pressure, or monitoring context. Because STT text can contain "
        "misrecognitions, avoid direct quotation in the final Korean title/description "
        "unless the wording is short, clear, and important. Prefer summarizing the "
        "meaning of suspicious or awkward STT phrases with wording such as `취지의 "
        "발언`, `표현`, or `언급` instead of reproducing them verbatim.\n\n"
    )

    if not any(segment.speaker for segment in struct_input.segments):
        return interpretation_note

    note = (
        "### SPEAKER ATTRIBUTION NOTE\n\n"
        "Use speaker labels in INPUT TEXT and SEGMENTS as the primary source for "
        "speaker attribution. Same speaker labels indicate the same speaker across "
        "turns. Do not use the raw labels in the final Korean summary. Do not merge "
        "adjacent utterances from different speaker labels into one speaker's continuous "
        "statement.\n\n"
    )
    role_note = (
        "### SPEAKER ROLE CONSISTENCY NOTE\n\n"
        "Relationship terms and self-references such as senior, junior, freshman, "
        "classmate, sunbae, hoobae, `선배`, `후배`, `신입생`, `내가`, or `저는` must "
        "stay attached to the speaker label that said them. Do not combine a refusal "
        "from one speaker with a relationship justification from another speaker into "
        "one person's continuous statement. If relationship-based wording appears in "
        "different speaker turns and the owner is unclear, omit the relationship label "
        "from the Korean summary and describe only the safer flow, such as that contact "
        "was refused and reasons were repeatedly requested or disputed. Avoid using "
        "relationship labels such as `선배`, `후배`, or `신입생` as the grammatical "
        "subject of the final Korean title/description when the same sentence can be "
        "written without a subject.\n\n"
    )
    single_speaker_note = _build_single_speaker_note(struct_input)
    transcript = _build_speaker_labeled_transcript(struct_input)
    if _full_text_has_speaker_labels(struct_input) or not transcript:
        return f"{interpretation_note}{note}{role_note}{single_speaker_note}"

    return (
        f"{interpretation_note}{note}{role_note}{single_speaker_note}"
        f"### SPEAKER-LABELED TRANSCRIPT (context only)\n\n{transcript}\n\n"
    )

def _build_single_speaker_note(struct_input: StructuringInput) -> str:
    speakers = {
        segment.speaker
        for segment in struct_input.segments
        if segment.speaker
    }
    if len(speakers) != 1:
        return ""

    return (
        "This STT input has one detected speaker only. Unless the input clearly says "
        "this is the victim's own voice memo, refer to this speaker as `상대방` in "
        "the final Korean summary. Do not use `화자`, `발화자`, `말한 사람`, or "
        "`한쪽` for this single-speaker voice evidence. For single-speaker call evidence, "
        "avoid centering the summary on isolated swear words and instead prioritize the "
        "overall contact or pressure flow when possible.\n\n"
    )

def _build_speaker_labeled_transcript(struct_input: StructuringInput) -> str:
    lines = []
    for segment in struct_input.segments:
        if not segment.speaker:
            continue
        start = f"{segment.start:.2f}"
        end = f"{segment.end:.2f}"
        lines.append(f"[{start}-{end}] {segment.speaker}: {segment.text}")

    return "\n".join(lines)

def _full_text_has_speaker_labels(struct_input: StructuringInput) -> bool:
    return any(
        segment.speaker and f"{segment.speaker}:" in struct_input.full_text
        for segment in struct_input.segments
    )

def build_complaint_document_messages(
    ai_input: ComplaintWritingAiInput,
) -> list[dict]:
    ai_input_json = json.dumps(ai_input.model_dump(mode="json"), ensure_ascii=False, indent=2)

    return [
        {
            "role": "system",
            "content": load_complaint_document_system_prompt(),
        },
        {
            "role": "user",
            "content": (
                "### STEP3 INPUT (json)\n\n"
                f"{ai_input_json}\n\n"
                "Write the complaint document sections strictly from the provided input."
            ),
        },
    ]

def build_damage_facts_statement_messages(
    ai_input: ComplaintWritingAiInput,
) -> list[dict]:
    ai_input_json = json.dumps(ai_input.model_dump(mode="json"), ensure_ascii=False, indent=2)

    return [
        {
            "role": "system",
            "content": load_damage_facts_statement_system_prompt(),
        },
        {
            "role": "user",
            "content": (
                "### STEP3 INPUT (json)\n\n"
                f"{ai_input_json}\n\n"
                "Write the damage facts statement strictly from the provided input."
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
        "For visible injury marks, describe only the visible bruise or discoloration itself, such as its body location, shape, and color. Do not mention fingers, hands, or nearby gestures, and do not add sentences saying the exact body part, cause, or timing cannot be confirmed.",
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

def build_victim_video_messages(
    *,
    frames: list[ExtractedVideoFrame],
    file_name: str | None = None,
) -> list[dict]:
    content: list[dict] = [
        {
            "type": "text",
            "text": "\n".join(
                [
                    "Analyze these still images from the same victim evidence video and return a single JSON object that follows the required schema.",
                    "All images come from one video evidence, so produce one combined result for the whole video.",
                    "Focus only on what is visually observable across the images.",
                    "Do not make medical, legal, or factual conclusions beyond the video images themselves.",
                    "In the final Korean description, use natural Korean wording such as `장면` instead of `프레임` when referring to video content.",
                    "Describe only the main incident action and the person performing it. Do not describe background people, vehicles, objects, or nearby actions that are not directly part of the incident.",
                    "Do not use arrows, step-by-step notation, or diagram-like phrasing in the final Korean description. Describe the incident flow only in natural sentence form.",
                    "If something is unclear, use cautious language and lower confidence.",
                    "For visible injury marks, describe only the visible bruise or discoloration itself, such as its body location, shape, and color. Do not mention fingers, hands, or nearby gestures, and do not add sentences saying the exact body part, cause, or timing cannot be confirmed.",
                    "Assign the `physical` tag only when bodily injury marks, bruising, bleeding, restraint, or strong physical force are comparatively clear in the images.",
                    "Do not assign the `physical` tag for simple touch or ambiguous contact alone.",
                    "Assign the `sexual_insult` tag only when sexual exposure, sexual humiliation, or unwanted sexual contact is comparatively clear in the frames.",
                    "Do not assign the `sexual_insult` tag when the sexual context is unclear or inferred only from pose or proximity.",
                    "Because this is a video-image input, evidence_span and evidence_anchor may be null when no reliable text span exists.",
                    *( [f"File name: {file_name}"] if file_name else [] ),
                ]
            ),
        }
    ]

    for frame in frames:
        content.append(
            {
                "type": "text",
                "text": f"Scene at {frame.frame_timestamp_seconds} seconds",
            }
        )
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": _build_image_data_url(
                        image_bytes=frame.path.read_bytes(),
                        mime_type=_infer_image_mime_type(
                            file_name=frame.path.name,
                            file_format="IMAGE",
                        ),
                    ),
                },
            }
        )

    return [
        {
            "role": "system",
            "content": load_system_prompt(),
        },
        {
            "role": "user",
            "content": content,
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