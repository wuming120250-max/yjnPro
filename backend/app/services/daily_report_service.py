from __future__ import annotations

import json
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.prompts import DAILY_REPORT_PROMPT
from app.models.ai_daily_report import AiDailyReport
from app.models.daily_revenue import DailyRevenue
from app.services.customer_service import current_biz_date
from app.services.menu_service import STAR, classify_menu
from app.services.qwen_service import QwenServiceError, generate_json
from app.services.recall_service import list_recall_customers
from app.services.table_service import peak_slot_summary


def _pct(current: float, previous: float) -> float:
    if not previous:
        return 0
    return round((current - previous) / previous * 100, 1)


def _score_revenue(change: float) -> int:
    if change > 10:
        return 30
    if change >= 5:
        return 25
    if change >= 0:
        return 20
    if change >= -5:
        return 10
    return 0


def _score_orders(change: float) -> int:
    if change > 8:
        return 20
    if change >= 0:
        return 14
    if change >= -8:
        return 8
    return 4


def _score_ticket(change: float) -> int:
    if change >= 3:
        return 15
    if change >= 0:
        return 12
    if change >= -3:
        return 8
    return 4


def build_scorecard(db: Session) -> dict:
    today = current_biz_date()
    rows = list(
        db.scalars(select(DailyRevenue).order_by(DailyRevenue.date.asc())).all()
    )
    by_date = {row.date: row for row in rows}
    today_row = by_date.get(today) or (rows[-1] if rows else None)
    yesterday = by_date.get(today - timedelta(days=1))
    last_week = by_date.get(today - timedelta(days=7))
    if today_row is None:
        raise ValueError("暂无今日营业数据")

    yesterday_revenue = float(yesterday.revenue) if yesterday else 0
    yesterday_orders = yesterday.order_count if yesterday else 0
    yesterday_aov = float(yesterday.average_order_amount) if yesterday else 0
    revenue_change = _pct(float(today_row.revenue), yesterday_revenue)
    order_change = _pct(today_row.order_count, yesterday_orders)
    aov_change = _pct(float(today_row.average_order_amount), yesterday_aov)
    week_change = _pct(float(today_row.revenue), float(last_week.revenue) if last_week else 0)

    menu = classify_menu(db)
    stars = [item for item in menu["items"] if item["quadrant"] == STAR]
    top_star = next((item for item in stars if item["name"] == "烤腱子肉"), stars[0] if stars else None)
    dish_score = 15 if top_star and top_star["sales_trend"] >= 10 else 10

    peak = peak_slot_summary(db, today)
    peak_score = 4 if peak["is_abnormal"] else 10
    recall_count = len(list_recall_customers(db))
    customer_score = 8 if recall_count else 10

    score = (
        _score_revenue(revenue_change)
        + _score_orders(order_change)
        + _score_ticket(aov_change)
        + dish_score
        + peak_score
        + customer_score
    )
    score = max(0, min(100, score))
    stars_label = "★" * max(1, min(5, round(score / 20))) + "☆" * (5 - max(1, min(5, round(score / 20))))

    return {
        "report_date": today.isoformat(),
        "score": score,
        "stars_label": stars_label,
        "today_revenue": float(today_row.revenue),
        "today_orders": today_row.order_count,
        "average_order_amount": float(today_row.average_order_amount),
        "yesterday_revenue": yesterday_revenue,
        "revenue_change": revenue_change,
        "order_change": order_change,
        "aov_change": aov_change,
        "week_change": week_change,
        "forecast_revenue": round(float(today_row.revenue) * 1.04, 0),
        "lunch_revenue": float(today_row.lunch_revenue),
        "dinner_revenue": float(today_row.dinner_revenue),
        "family_orders": today_row.family_orders,
        "menu_counts": menu["counts"],
        "top_star": top_star,
        "peak": peak,
        "recall_count": recall_count,
        "score_detail": {
            "revenue": _score_revenue(revenue_change),
            "orders": _score_orders(order_change),
            "ticket": _score_ticket(aov_change),
            "dish": dish_score,
            "peak": peak_score,
            "customer": customer_score,
        },
    }


def diagnosis_items(card: dict) -> list[dict]:
    items = []
    peak = card["peak"]
    if peak["is_abnormal"]:
        items.append(
            {
                "level": "critical",
                "title": f"晚餐 {peak['label']} 订单效率下降",
                "detail": f"平均用餐 {peak['avg_duration']} 分钟，正常 {peak['normal_duration']} 分钟。",
                "reason": "高峰期出餐压力增加。",
                "suggestion": "重点检查热门菜出餐时间。",
                "link": "/table-efficiency",
            }
        )
    star = card["top_star"]
    if star:
        items.append(
            {
                "level": "positive",
                "title": f"{star['name']}销量较上周同期上涨 {star['sales_trend']:.0f}%",
                "detail": f"毛利率 {star['gross_margin']}%，属于高毛利菜品。",
                "reason": "销量高且利润好。",
                "suggestion": "继续作为重点推荐菜。",
                "link": "/menu-analysis",
            }
        )
    items.append(
        {
            "level": "opportunity",
            "title": "家庭聚餐订单近期增长",
            "detail": f"今日家庭聚餐相关订单 {card['family_orders']} 单。",
            "reason": "周末家庭客群需求上升。",
            "suggestion": "设计 4～6 人家庭聚餐套餐。",
            "link": "/marketing",
        }
    )
    return items


def _demo_ai(card: dict) -> dict:
    star_name = card["top_star"]["name"] if card["top_star"] else "招牌菜"
    return {
        "summary": (
            f"今日营业额 {card['today_revenue']:.0f} 元，较昨日 {card['revenue_change']:+.1f}%。"
            f"整体经营正常，但晚餐高峰翻台偏慢，{star_name}表现突出。"
        ),
        "warnings": ["晚餐高峰效率下降，平均用餐时间偏长。"],
        "positives": [f"{star_name}销量与毛利双高，值得继续主推。"],
        "opportunities": ["家庭聚餐需求增加，可做 4～6 人套餐。"],
        "recommendation": "重点推广家庭聚餐套餐",
        "demo_fallback": True,
    }


async def generate_daily_report(db: Session) -> dict:
    card = build_scorecard(db)
    prompt = DAILY_REPORT_PROMPT.format(ops_data=json.dumps(card, ensure_ascii=False, default=str))
    try:
        ai = await generate_json(prompt)
        ai["demo_fallback"] = False
    except QwenServiceError:
        ai = _demo_ai(card)
    payload = {
        **card,
        "summary": ai.get("summary") or "",
        "warnings": ai.get("warnings") or [],
        "positives": ai.get("positives") or [],
        "opportunities": ai.get("opportunities") or [],
        "recommendation": ai.get("recommendation") or "重点推广家庭聚餐套餐",
        "diagnosis": diagnosis_items(card),
        "demo_fallback": bool(ai.get("demo_fallback")),
    }
    record = db.scalars(
        select(AiDailyReport).where(AiDailyReport.report_date == current_biz_date())
    ).first()
    warnings = json.dumps(payload["warnings"], ensure_ascii=False)
    positives = json.dumps(payload["positives"], ensure_ascii=False)
    opportunities = json.dumps(payload["opportunities"], ensure_ascii=False)
    if record:
        record.score = payload["score"]
        record.summary = payload["summary"]
        record.warnings = warnings
        record.positive_findings = positives
        record.opportunities = opportunities
        record.recommendation = payload["recommendation"]
    else:
        db.add(
            AiDailyReport(
                report_date=current_biz_date(),
                score=payload["score"],
                summary=payload["summary"],
                warnings=warnings,
                positive_findings=positives,
                opportunities=opportunities,
                recommendation=payload["recommendation"],
            )
        )
    db.commit()
    return payload


def _as_list(raw: str) -> list:
    try:
        data = json.loads(raw or "[]")
        if isinstance(data, list):
            return data
        if isinstance(data, str) and data:
            return [data]
        return []
    except json.JSONDecodeError:
        return [raw] if raw else []


def get_daily_report(db: Session) -> dict:
    card = build_scorecard(db)
    record = db.scalars(
        select(AiDailyReport).where(AiDailyReport.report_date == current_biz_date())
    ).first()
    if record:
        return {
            **card,
            "summary": record.summary,
            "warnings": _as_list(record.warnings),
            "positives": _as_list(record.positive_findings),
            "opportunities": _as_list(record.opportunities),
            "recommendation": record.recommendation,
            "diagnosis": diagnosis_items(card),
            "demo_fallback": False,
        }
    demo = _demo_ai(card)
    return {
        **card,
        **demo,
        "diagnosis": diagnosis_items(card),
        "recommendation": demo["recommendation"],
    }
