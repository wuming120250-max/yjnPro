from __future__ import annotations

import json
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.prompts import REVENUE_ANALYZE_PROMPT
from app.models.daily_revenue import DailyRevenue
from app.services.customer_service import current_biz_date
from app.services.qwen_service import QwenServiceError, generate_json


def list_revenue(db: Session, days: int = 30) -> list[dict]:
    rows = list(db.scalars(select(DailyRevenue).order_by(DailyRevenue.date.asc())).all())
    if days:
        rows = rows[-days:]
    return [
        {
            "date": row.date.isoformat(),
            "revenue": float(row.revenue),
            "order_count": row.order_count,
            "average_order_amount": float(row.average_order_amount),
            "lunch_revenue": float(row.lunch_revenue),
            "dinner_revenue": float(row.dinner_revenue),
            "banquet_revenue": float(row.banquet_revenue),
            "lunch_orders": row.lunch_orders,
            "dinner_orders": row.dinner_orders,
            "family_orders": row.family_orders,
        }
        for row in rows
    ]


def detect_anomaly(db: Session) -> dict:
    today = current_biz_date()
    rows = list_revenue(db, 30)
    today_row = next((item for item in rows if item["date"] == today.isoformat()), rows[-1] if rows else None)
    if today_row is None:
        raise ValueError("暂无营业数据")
    window = [item for item in rows if item["date"] != today_row["date"]][-7:]
    avg7 = sum(item["revenue"] for item in window) / len(window) if window else today_row["revenue"]
    change = round((today_row["revenue"] - avg7) / avg7 * 100, 1) if avg7 else 0
    yesterday = next(
        (item for item in rows if item["date"] == (today - timedelta(days=1)).isoformat()),
        None,
    )
    worst = min(rows, key=lambda item: item["revenue"]) if rows else today_row
    dinner_drop = False
    if yesterday and yesterday["dinner_orders"]:
        dinner_drop = (
            (today_row["dinner_orders"] - yesterday["dinner_orders"]) / yesterday["dinner_orders"] * 100
        )
    is_anomaly = float(worst["revenue"]) < avg7 * 0.9
    worst_drop = round((worst["revenue"] - avg7) / avg7 * 100, 1) if avg7 else 0
    return {
        "today": today_row,
        "yesterday": yesterday,
        "avg7": round(avg7, 0),
        "change_vs_avg7": change,
        "worst_day": worst,
        "worst_drop": worst_drop,
        "is_anomaly": bool(is_anomaly or (isinstance(dinner_drop, float) and dinner_drop <= -15)),
        "dinner_order_change": round(dinner_drop, 1) if isinstance(dinner_drop, float) else 0,
        "items": rows,
    }


def _demo_analyze(payload: dict) -> dict:
    worst = payload["worst_day"]
    return {
        "is_anomaly": True,
        "verdict": f"近期出现明显营业额下滑，最低一天为 {worst['date']} 的 ¥{worst['revenue']:.0f}。",
        "main_reason": "晚餐客流下降，而不是消费能力下降。",
        "reasons": [
            "晚餐订单下降约 18%",
            "4～6 人家庭聚餐订单下降约 21%",
            "客单价变化不明显",
            "午餐表现正常",
        ],
        "traffic_or_ticket": "客流问题",
        "key_period": "晚餐",
        "key_customer": "家庭聚餐客群",
        "tomorrow_action": "明天重点推广家庭聚餐场景，而不是单纯降低价格。",
        "demo_fallback": True,
    }


async def analyze_revenue(db: Session) -> dict:
    payload = detect_anomaly(db)
    prompt = REVENUE_ANALYZE_PROMPT.format(revenue_data=json.dumps(payload, ensure_ascii=False))
    try:
        result = await generate_json(prompt)
        result["demo_fallback"] = False
    except QwenServiceError:
        result = _demo_analyze(payload)
    result["metrics"] = payload
    return result
