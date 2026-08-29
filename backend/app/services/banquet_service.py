from __future__ import annotations

import json
from typing import Any

from sqlalchemy import nulls_last, select
from sqlalchemy.orm import Session

from app.core.prompts import BANQUET_ANALYZE_PROMPT
from app.models.ai_analysis import AiAnalysis
from app.models.banquet_lead import BanquetLead
from app.services.qwen_service import QwenServiceError, generate_json


def list_leads(db: Session, status: str | None = None) -> list[BanquetLead]:
    stmt = select(BanquetLead).order_by(nulls_last(BanquetLead.event_date.asc()), BanquetLead.id.desc())
    if status:
        stmt = stmt.where(BanquetLead.status == status)
    return list(db.scalars(stmt).all())


def get_lead(db: Session, lead_id: int) -> BanquetLead | None:
    return db.get(BanquetLead, lead_id)


def create_lead(db: Session, payload: dict[str, Any]) -> BanquetLead:
    lead = BanquetLead(**payload)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def update_lead(db: Session, lead_id: int, payload: dict[str, Any]) -> BanquetLead | None:
    lead = get_lead(db, lead_id)
    if lead is None:
        return None
    for key, value in payload.items():
        if value is not None:
            setattr(lead, key, value)
    db.commit()
    db.refresh(lead)
    return lead


def _demo_analyze(lead: BanquetLead) -> dict[str, Any]:
    people = lead.people_count
    high_value = people >= 20 or "5000" in lead.expected_amount or "8000" in lead.expected_amount
    score = 5 if people >= 20 else (4 if people >= 10 else 3)
    potential = "高" if high_value else "中"
    name = lead.customer_name
    return {
        "customer_value": "★" * score,
        "customer_value_score": score,
        "deal_potential": potential,
        "reason": (
            f"人数{'较多' if people >= 20 else '适中'}，预算{lead.expected_amount}，"
            f"活动时间{'明确' if lead.event_date else '待确认'}。"
            f"{'属于高客单价宴请线索，应优先跟进。' if high_value else '有成交空间，建议尽快确认档期与菜单。'}"
        ),
        "followup_suggestion": "24小时内主动跟进，确认人数、预算和忌口。" if high_value else "本周内电话或微信跟进一次。",
        "next_step": "提供2套套餐方案，并预留包间档期。" if people >= 15 else "发送菜单与包间照片，约定到店看场。",
        "script": (
            f"{name}您好，我是宴江南汇海路店的。看到您咨询{lead.event_type}，大概{people}位。"
            "我们这边包间可以满足，也准备了两套不同价位的套餐方案，您看方便的时候我发您，或者您过来看一下场地？"
        ),
        "demo_fallback": True,
    }


async def analyze_lead(db: Session, lead_id: int) -> dict[str, Any]:
    lead = get_lead(db, lead_id)
    if lead is None:
        raise ValueError("线索不存在")
    prompt = BANQUET_ANALYZE_PROMPT.format(
        customer_name=lead.customer_name,
        event_type=lead.event_type,
        people_count=lead.people_count,
        expected_amount=lead.expected_amount,
        event_date=lead.event_date or "待定",
        source=lead.source,
        status=lead.status,
        notes=lead.notes or "无",
    )
    try:
        result = await generate_json(prompt)
        result["demo_fallback"] = False
    except QwenServiceError:
        result = _demo_analyze(lead)
    record = AiAnalysis(
        analysis_type="banquet_followup",
        target_id=str(lead_id),
        input_data=json.dumps({"prompt": prompt}, ensure_ascii=False, default=str),
        result=json.dumps(result, ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    return result
