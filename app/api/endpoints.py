from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas  # 导入 schemas 目录
from ..db import models
from ..db.session import SessionLocal
router = APIRouter()
import json

# 我们将在这里添加所有API端点
# Dependency: 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/consultations", response_model=schemas.consultation.Consultation)
def create_consultation(
    *,
    db: Session = Depends(get_db),
    consultation_in: schemas.consultation.ConsultationCreate
):
    """
    创建一个新的咨询记录。
    """
    # 1. 验证 consent
    if not consultation_in.consent_given:
        raise HTTPException(
            status_code=403,
            detail="Consent must be given to start a consultation."
        )

    # 2. 将 Pydantic Schema 对象转换为 SQLAlchemy Model 对象
    db_consultation = models.Consultation(
        patient_id=consultation_in.patient_id,
        consent_given=consultation_in.consent_given
    )

    # 3. 写入数据库
    db.add(db_consultation)  # 添加到会话
    db.commit()             # 提交事务，写入数据库
    db.refresh(db_consultation) # 刷新实例，获取数据库生成的数据（如ID）

    return db_consultation

# ... (文件顶部的 imports 和 create_consultation 函数保持不变) ...
from ..core import summarization, redaction
import re
import json # 确保导入了json

@router.post("/consultations/{consultation_id}/process", response_model=schemas.consultation.Consultation)
def process_consultation_transcript(
        *,
        db: Session = Depends(get_db),
        consultation_id: int,
        transcript_in: schemas.consultation.TranscriptProcessRequest
):
    db_consultation = db.query(models.Consultation).filter(models.Consultation.id == consultation_id).first()
    if not db_consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    db_consultation.raw_transcript = transcript_in.transcript

    # 接收摘要数据和位置地图
    summary_data, location_map = summarization.generate_summaries_from_text(transcript_in.transcript)
    if not summary_data:
        raise HTTPException(status_code=500, detail="Failed to generate summary from LLM")

    all_summaries_content = {
        'clinician': json.dumps(summary_data.get('clinician_summary', {})),
        'patient': json.dumps(summary_data.get('patient_summary', {}))
    }

    for summary_type, content_str in all_summaries_content.items():
        db_summary = models.Summary(consultation_id=consultation_id, summary_type=summary_type, content=content_str)
        db.add(db_summary)
        db.flush()

        citation_blocks = re.findall(r'\[S[^\]]*\]', content_str)
        all_anchor_numbers = []
        for block in citation_blocks:
            numbers = re.findall(r'\d+', block)
            all_anchor_numbers.extend(numbers)

        for anchor_num_str in all_anchor_numbers:
            anchor_num = int(anchor_num_str)
            # 从地图中查找位置
            source_location = location_map.get(anchor_num, {"start": 0, "end": 0})

            db_anchor = models.ProvenanceAnchor(
                summary_id=db_summary.id,
                anchor_id=f"S{anchor_num}",
                # 使用查找到的真实位置！
                source_span_start=source_location["start"],
                source_span_end=source_location["end"]
            )
            db.add(db_anchor)

    db.commit()
    db.refresh(db_consultation)
    return db_consultation