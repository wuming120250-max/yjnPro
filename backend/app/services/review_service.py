from __future__ import annotations

import json
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.prompts import REVIEW_ANALYZE_PROMPT
from app.models.ai_analysis import AiAnalysis
from app.models.review import Review
from app.services.qwen_service import QwenServiceError, generate_json


def list_reviews(db: Session, sentiment: str | None = None, source: str | None = None) -> list[Review]:
    stmt = select(Review).order_by(Review.review_date.desc(), Review.id.desc())
    if sentiment:
        stmt = stmt.where(Review.sentiment == sentiment)
    if source:
        stmt = stmt.where(Review.source == source)
    return list(db.scalars(stmt).all())


def review_stats(db: Session) -> dict[str, Any]:
    total = db.scalar(select(func.count(Review.id))) or 0
    avg = db.scalar(select(func.avg(Review.rating))) or 0
    positive = db.scalar(select(func.count(Review.id)).where(Review.sentiment == "好评")) or 0
    negative = db.scalar(select(func.count(Review.id)).where(Review.sentiment == "差评")) or 0
    return {
        "total": total,
        "average_rating": round(float(avg), 1) if total else 0,
        "positive_rate": round(positive / total * 100, 1) if total else 0,
        "negative_rate": round(negative / total * 100, 1) if total else 0,
    }


def _demo_analysis() -> dict[str, Any]:
    return {
        "likes": ["菜品口味", "海鲜新鲜", "环境舒适", "适合家庭聚餐", "服务态度"],
        "complaints": ["高峰期上菜速度", "高峰期服务响应", "个别菜品价格"],
        "focus": ["菜品品质", "出餐效率", "聚餐氛围", "性价比"],
        "hot_dishes": ["特色海鲜", "清蒸鲈鱼", "蒜蓉粉丝扇贝", "红烧肉"],
        "hot_scenes": ["家庭聚餐", "朋友小聚", "商务宴请"],
        "service_issues": ["周末晚餐高峰上菜偏慢", "高峰时段找服务员等待时间偏长"],
        "suggestions": [
            {
                "finding": "「家庭聚餐」出现频率较高。",
                "suggestion": "打造4～6人家庭聚餐套餐，作为周末主推。",
            },
            {
                "finding": "「海鲜」是高频正向关键词。",
                "suggestion": "在营销内容中强化海鲜新鲜、现做现蒸的特色。",
            },
            {
                "finding": "高峰期「上菜慢」出现多次。",
                "suggestion": "针对周末晚餐高峰优化出餐流程，并提前告知预估等待时间。",
            },
        ],
        "demo_fallback": True,
    }


async def analyze_reviews(db: Session) -> dict[str, Any]:
    reviews = list_reviews(db)
    lines = [
        f"{item.review_date} | {item.source} | {item.rating}分 | {item.sentiment} | {item.content}"
        for item in reviews[:80]
    ]
    prompt = REVIEW_ANALYZE_PROMPT.format(reviews_text="\n".join(lines) or "暂无评价")
    try:
        result = await generate_json(prompt)
        result["demo_fallback"] = False
        if "suggestions" in result:
            normalized = []
            for item in result["suggestions"]:
                if isinstance(item, dict):
                    normalized.append(
                        {
                            "finding": item.get("finding") or item.get("发现") or "",
                            "suggestion": item.get("suggestion") or item.get("建议") or "",
                        }
                    )
                else:
                    normalized.append({"finding": str(item), "suggestion": ""})
            result["suggestions"] = normalized
    except QwenServiceError:
        result = _demo_analysis()
    record = AiAnalysis(
        analysis_type="review_analysis",
        target_id="all",
        input_data=json.dumps({"count": len(reviews)}, ensure_ascii=False),
        result=json.dumps(result, ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    return result
