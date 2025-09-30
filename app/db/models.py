import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .session import Base # 从我们刚刚创建的 session.py 中导入 Base

class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True, nullable=False)
    consent_given = Column(Boolean, nullable=False)
    raw_transcript = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # 建立与 Summary 模型的关系
    # 一个 Consultation 可以有多个 Summary
    summaries = relationship("Summary", back_populates="consultation")

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"))
    summary_type = Column(String, nullable=False) # 'clinician' or 'patient'
    content = Column(String, nullable=False)

    # 建立与 Consultation 模型的关系
    consultation = relationship("Consultation", back_populates="summaries")
    # 建立与 ProvenanceAnchor 模型的关系
    anchors = relationship("ProvenanceAnchor", back_populates="summary")


class ProvenanceAnchor(Base):
    __tablename__ = "provenance_anchors"

    id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(Integer, ForeignKey("summaries.id"))
    anchor_id = Column(String, nullable=False) # e.g., 'S1', 'S2'
    source_span_start = Column(Integer, nullable=False)
    source_span_end = Column(Integer, nullable=False)

    # 建立与 Summary 模型的关系
    summary = relationship("Summary", back_populates="anchors")