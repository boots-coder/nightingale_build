from pydantic import BaseModel
import datetime
from typing import List

# --- ProvenanceAnchor Schemas ---
class ProvenanceAnchorBase(BaseModel):
    anchor_id: str
    source_span_start: int
    source_span_end: int

class ProvenanceAnchorCreate(ProvenanceAnchorBase):
    pass

class ProvenanceAnchor(ProvenanceAnchorBase):
    id: int
    summary_id: int

    class Config:
        orm_mode = True

# --- Summary Schemas ---
class SummaryBase(BaseModel):
    summary_type: str
    content: str

class SummaryCreate(SummaryBase):
    pass

class Summary(SummaryBase):
    id: int
    consultation_id: int
    anchors: List[ProvenanceAnchor] = [] # 返回Summary时，嵌套返回其下的Anchors

    class Config:
        orm_mode = True

# --- Consultation Schemas ---
class ConsultationBase(BaseModel):
    patient_id: str
    consent_given: bool

class ConsultationCreate(ConsultationBase):
    pass

# 更新这个Schema来包含summaries
class Consultation(ConsultationBase):
    id: int
    raw_transcript: str | None = None
    created_at: datetime.datetime
    summaries: List[Summary] = [] # 返回Consultation时，嵌套返回其下的Summaries

    class Config:
        orm_mode = True

# --- 新增一个用于接收Transcript的Schema ---
class TranscriptProcessRequest(BaseModel):
    transcript: str