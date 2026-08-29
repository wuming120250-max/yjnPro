from __future__ import annotations

import json
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.business_opportunity import BusinessOpportunity
from app.services.customer_service import current_biz_date
from app.services.opportunities.opportunity_detector import detect_opportunities
from app.services.opportunities.opportunity_prompts import ANALYZE_PROMPT, TODAY_FOCUS_PROMPT
from app.services.opportunities.opportunity_scorer import score_opportunity
from app.services.qwen_service import QwenServiceError, generate_json

logger = logging.getLogger(__name__)

TYPE_LABELS = {
    "revenue": "营业机会",
    "menu": "菜品机会",
    "customer": "客户机会",
    "service": "服务机会",
    "banquet": "宴请机会",
}
LEVEL_LABELS = {"high": "高优先级", "medium": "中优先级", "low": "普通机会"}
STATUS_LABELS = {
    "pending": "待处理",
    "processing": "处理中",
    "completed": "已完成",
    "ignored": "已忽略",
}
IMPACT_LABELS = {
    "revenue": "营业额",
    "cost": "成本",
    "efficiency": "效率",
    "customer": "客户",
}


def serialize_opportunity(item: BusinessOpportunity) -> dict:
    snapshot = item.data_snapshot if isinstance(item.data_snapshot, dict) else {}
    return {
        "id": item.id,
        "opportunity_key": item.opportunity_key,
        "title": item.title,
        "type": item.type,
        "type_label": TYPE_LABELS.get(item.type, item.type),
        "priority": item.priority,
        "level": item.level,
        "level_label": LEVEL_LABELS.get(item.level, item.level),
        "description": item.description,
        "data_source": item.data_source,
        "data_snapshot": snapshot,
        "reason": item.reason,
        "estimated_impact": item.estimated_impact,
        "impact_type": item.impact_type,
        "impact_type_label": IMPACT_LABELS.get(item.impact_type, item.impact_type),
        "suggestion": item.suggestion,
        "action": item.action,
        "summary": item.summary,
        "link": item.link,
        "status": item.status,
        "status_label": STATUS_LABELS.get(item.status, item.status),
        "is_today_focus": item.is_today_focus,
        "due_date": item.due_date.isoformat() if item.due_date else None,
        "completed_at": item.completed_at.isoformat() if item.completed_at else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "action_items": snapshot.get("action_items") or [],
        "demo_note": snapshot.get("note") or "",
    }


def _apply_candidate(record: BusinessOpportunity, candidate: dict, priority: int, level: str) -> None:
    snapshot = dict(candidate.get("data_snapshot") or {})
    snapshot["action_items"] = candidate.get("action_items") or []
    record.title = candidate["title"]
    record.type = candidate["type"]
    record.priority = priority
    record.level = level
    record.description = candidate.get("description") or ""
    record.data_source = candidate.get("data_source") or ""
    record.data_snapshot = snapshot
    record.reason = candidate.get("reason") or ""
    record.estimated_impact = float(candidate.get("estimated_impact") or 0)
    record.impact_type = candidate.get("impact_type") or "revenue"
    record.suggestion = candidate.get("suggestion") or ""
    record.action = candidate.get("action") or ""
    record.summary = candidate.get("summary") or ""
    record.link = candidate.get("link") or ""
    record.due_date = current_biz_date()


def stats_for(db: Session) -> dict:
    rows = list(db.scalars(select(BusinessOpportunity)).all())
    return {
        "total": len(rows),
        "high": sum(1 for row in rows if row.level == "high" and row.status != "ignored"),
        "medium": sum(1 for row in rows if row.level == "medium" and row.status != "ignored"),
        "low": sum(1 for row in rows if row.level == "low" and row.status != "ignored"),
        "completed": sum(1 for row in rows if row.status == "completed"),
        "pending": sum(1 for row in rows if row.status == "pending"),
        "processing": sum(1 for row in rows if row.status == "processing"),
    }


def list_opportunities(
    db: Session,
    *,
    type: str | None = None,
    level: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    query = select(BusinessOpportunity)
    if type:
        query = query.where(BusinessOpportunity.type == type)
    if level:
        query = query.where(BusinessOpportunity.level == level)
    if status:
        query = query.where(BusinessOpportunity.status == status)
    query = query.order_by(
        BusinessOpportunity.is_today_focus.desc(),
        BusinessOpportunity.priority.desc(),
        BusinessOpportunity.id.asc(),
    )
    rows = list(db.scalars(query).all())
    total = len(rows)
    start = max(page - 1, 0) * page_size
    items = rows[start : start + page_size]
    return {
        "total": total,
        "items": [serialize_opportunity(item) for item in items],
        "stats": stats_for(db),
        "today_priority": serialize_opportunity(today_focus(db)) if today_focus(db) else None,
        "biz_date": current_biz_date().isoformat(),
        "demo_mode": get_settings().demo_mode,
    }


def get_opportunity(db: Session, opp_id: int) -> BusinessOpportunity | None:
    return db.get(BusinessOpportunity, opp_id)


def today_focus(db: Session) -> BusinessOpportunity | None:
    focused = db.scalars(
        select(BusinessOpportunity)
        .where(BusinessOpportunity.is_today_focus.is_(True))
        .where(BusinessOpportunity.status.in_(["pending", "processing"]))
        .order_by(BusinessOpportunity.priority.desc())
    ).first()
    if focused:
        return focused
    return db.scalars(
        select(BusinessOpportunity)
        .where(BusinessOpportunity.status.in_(["pending", "processing"]))
        .order_by(BusinessOpportunity.priority.desc())
    ).first()


def top_opportunities(db: Session, limit: int = 3) -> list[dict]:
    rows = list(
        db.scalars(
            select(BusinessOpportunity)
            .where(BusinessOpportunity.status.in_(["pending", "processing"]))
            .order_by(BusinessOpportunity.priority.desc())
            .limit(limit)
        ).all()
    )
    return [serialize_opportunity(item) for item in rows]


async def generate_opportunities(db: Session, *, force: bool = False) -> dict:
    logger.info("opportunity generation started")
    candidates = detect_opportunities(db)
    saved: list[BusinessOpportunity] = []
    for candidate in candidates:
        priority, level = score_opportunity(
            estimated_impact=float(candidate.get("estimated_impact") or 0),
            score_inputs=candidate.get("score_inputs"),
        )
        existing = db.scalars(
            select(BusinessOpportunity).where(
                BusinessOpportunity.opportunity_key == candidate["opportunity_key"]
            )
        ).first()
        if existing and existing.status in {"completed", "ignored"} and not force:
            saved.append(existing)
            continue
        if existing and not force and existing.status in {"pending", "processing"}:
            _apply_candidate(existing, candidate, priority, level)
            saved.append(existing)
            continue
        if existing and force:
            _apply_candidate(existing, candidate, priority, level)
            existing.status = "pending"
            existing.completed_at = None
            existing.is_today_focus = False
            saved.append(existing)
            continue
        record = BusinessOpportunity(opportunity_key=candidate["opportunity_key"], status="pending")
        _apply_candidate(record, candidate, priority, level)
        db.add(record)
        saved.append(record)
    db.flush()

    for row in saved:
        row.is_today_focus = False
    focus = max(
        (row for row in saved if row.status in {"pending", "processing"}),
        key=lambda row: row.priority,
        default=None,
    )
    demo_fallback = True
    try:
        compact = [
            {
                "opportunity_key": row.opportunity_key,
                "title": row.title,
                "type": row.type,
                "priority": row.priority,
                "level": row.level,
                "estimated_impact": row.estimated_impact,
                "description": row.description,
            }
            for row in saved
            if row.status in {"pending", "processing"}
        ]
        picked = await generate_json(
            TODAY_FOCUS_PROMPT.format(opportunities=json.dumps(compact, ensure_ascii=False))
        )
        key = picked.get("opportunity_key")
        chosen = next((row for row in saved if row.opportunity_key == key), None)
        if chosen:
            focus = chosen
            if picked.get("reason"):
                focus.reason = str(picked["reason"])
            if picked.get("suggestion"):
                focus.suggestion = str(picked["suggestion"])
        demo_fallback = False
        logger.info("opportunity generation used Qwen for today focus")
    except QwenServiceError as exc:
        logger.info("opportunity generation fallback to rules: %s", exc)

    if focus:
        focus.is_today_focus = True
    db.commit()
    for row in saved:
        db.refresh(row)
    logger.info("opportunity generation finished, count=%s", len(saved))
    return {
        **list_opportunities(db),
        "generated": len(saved),
        "demo_fallback": demo_fallback,
    }


async def analyze_opportunity(db: Session, opp_id: int) -> dict:
    record = get_opportunity(db, opp_id)
    if record is None:
        raise ValueError("机会不存在")
    prompt = ANALYZE_PROMPT.format(
        type=TYPE_LABELS.get(record.type, record.type),
        title=record.title,
        data=json.dumps(
            {
                "description": record.description,
                "snapshot": record.data_snapshot,
                "estimated_impact": record.estimated_impact,
            },
            ensure_ascii=False,
        ),
    )
    demo_fallback = False
    try:
        result = await generate_json(prompt)
        record.summary = str(result.get("summary") or record.summary)
        record.reason = str(result.get("reason") or record.reason)
        record.suggestion = str(result.get("suggestion") or record.suggestion)
        record.action = str(result.get("action") or record.action)
        logger.info("opportunity analyze id=%s", record.id)
    except QwenServiceError:
        demo_fallback = True
        logger.info("opportunity analyze fallback id=%s", record.id)
    db.commit()
    db.refresh(record)
    payload = serialize_opportunity(record)
    payload["demo_fallback"] = demo_fallback
    return payload


def set_processing(db: Session, opp_id: int) -> dict:
    record = get_opportunity(db, opp_id)
    if record is None:
        raise ValueError("机会不存在")
    record.status = "processing"
    db.commit()
    db.refresh(record)
    return serialize_opportunity(record)


def complete_opportunity(db: Session, opp_id: int) -> dict:
    record = get_opportunity(db, opp_id)
    if record is None:
        raise ValueError("机会不存在")
    record.status = "completed"
    record.completed_at = datetime.now()
    db.commit()
    db.refresh(record)
    return serialize_opportunity(record)


def ignore_opportunity(db: Session, opp_id: int) -> dict:
    record = get_opportunity(db, opp_id)
    if record is None:
        raise ValueError("机会不存在")
    record.status = "ignored"
    if record.is_today_focus:
        record.is_today_focus = False
    db.commit()
    db.refresh(record)
    return serialize_opportunity(record)
