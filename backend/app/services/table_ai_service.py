from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.core.prompts import TABLE_ANALYZE_PROMPT
from app.services.qwen_service import QwenServiceError, generate_json
from app.services.table_service import NORMAL_DURATION, list_slots, peak_slot_summary


def get_table_efficiency(db: Session) -> dict:
    slots = list_slots(db)
    peak = peak_slot_summary(db)
    return {
        "note": "以上翻台数据为 Demo 模拟数据，用于演示高峰效率诊断，并非宴江南真实桌台数据。",
        "normal_duration": NORMAL_DURATION,
        "peak": peak,
        "slots": slots,
    }


def _demo(peak: dict) -> dict:
    return {
        "verdict": "高峰期桌台周转效率偏低。",
        "peak_issue": (
            f"{peak['label']} 平均用餐 {peak['avg_duration']} 分钟，正常 {peak['normal_duration']} 分钟。"
        ),
        "normal_duration": peak["normal_duration"],
        "suggestions": ["检查出餐速度", "优化加菜流程", "缩短结账等待"],
        "demo_fallback": True,
    }


async def analyze_table_efficiency(db: Session) -> dict:
    data = get_table_efficiency(db)
    prompt = TABLE_ANALYZE_PROMPT.format(table_data=json.dumps(data, ensure_ascii=False))
    try:
        result = await generate_json(prompt)
        result["demo_fallback"] = False
    except QwenServiceError:
        result = _demo(data["peak"])
    result["metrics"] = data
    return result
