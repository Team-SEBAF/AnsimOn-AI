from pydantic import BaseModel
from typing import List, Optional, Literal

class StructuringSegment(BaseModel):
    text: str
    start: float
    end: float

class StructuringInput(BaseModel):
    modality: Literal["text"]
    source_type: Literal["stt"]
    language: Optional[str]
    full_text: str
    segments: List[StructuringSegment]