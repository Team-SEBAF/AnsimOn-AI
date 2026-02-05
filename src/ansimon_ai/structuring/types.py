from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any

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

class AnchorStats(BaseModel):
    total_spans: int
    matched_spans: int
    partial_matched_spans: int
    unmatched_spans: int
    notes: Optional[str] = None

class VlidationResult(BaseModel):
    status: Literal["PASS", "FAIL", "WARN"]
    error_codes: List[str]
    message: Optional[str] = None

class StructuringResult(BaseModel):
    output_json: Dict[str, Any]
    cache_hit: bool
    anchor_stats: AnchorStats
    validation: VlidationResult
    run_id: Optional[str] = None