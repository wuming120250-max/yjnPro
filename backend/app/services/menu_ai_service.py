from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.prompts import MENU_DIAGNOSE_PROMPT
from app.services.menu_service import classify_menu
from app.services.qwen_service import QwenServiceError, generate_json


def get_menu_analysis(db: Session) -> dict:
    return classify_menu(db)


def _demo_diagnosis(data: dict) -> dict:
    stars = [item["name"] for item in data["items"] if item["quadrant"] == "明星菜"][:4]
    pots = [item["name"] for item in data["items"] if item["quadrant"] == "潜力菜"][:4]
    traffic = [item["name"] for item in data["items"] if item["quadrant"] == "引流菜"][:4]
    elim = [item["name"] for item in data["items"] if item["quadrant"] == "淘汰候选"][:4]
    return {
        "health_score": 78,
        "judgment": "当前菜单整体结构正常，但存在部分低销量低毛利菜品。建议进一步优化菜单结构。",
        "stars": [f"{name}：高销量 + 高毛利" for name in stars] or ["烤腱子肉：高销量 + 高毛利"],
        "potentials": [f"{name}：高毛利但销量偏低，建议服务员重点推荐" for name in pots]
        or ["砂锅荔浦芋头：高毛利但销量偏低"],
        "traffic": [f"{name}：销量高但毛利偏低，不宜过度依赖" for name in traffic],
        "eliminate": [f"{name}：销量低 + 毛利低，考虑优化或下架" for name in elim],
        "structure_issue": "高毛利潜力菜曝光不足，部分低毛利菜占用菜单位置。",
        "suggestions": [
            "将高毛利潜力菜加入服务员推荐话术。",
            "继续主推烤腱子肉等明星菜。",
            "评估低销低毛利菜是否换菜或调价。",
        ],
        "demo_fallback": True,
    }


async def diagnose_menu(db: Session) -> dict:
    data = classify_menu(db)
    compact = [
        {
            "name": item["name"],
            "sales_count": item["sales_count"],
            "gross_margin": item["gross_margin"],
            "sales_trend": item["sales_trend"],
            "quadrant": item["quadrant"],
        }
        for item in data["items"]
    ]
    prompt = MENU_DIAGNOSE_PROMPT.format(menu_data=json.dumps(compact, ensure_ascii=False))
    try:
        result = await generate_json(prompt)
        result["demo_fallback"] = False
    except QwenServiceError:
        result = _demo_diagnosis(data)
    result["counts"] = data["counts"]
    return result
