from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.core.prompts import STAFF_RECOMMEND_PROMPT
from app.services.menu_service import STAR, classify_menu
from app.services.qwen_service import QwenServiceError, generate_json


def _pick_demo(data: dict, people: int, budget: int, scene: str, mode: str) -> list[str]:
    if scene == "家庭聚餐" or people <= 4:
        preferred = ["碟鱼头", "凤梨虾球", "芹菜拌海米", "特色例汤"]
    elif scene == "商务宴请":
        preferred = ["清蒸鲈鱼", "烤腱子肉", "葱油鲍鱼", "特色例汤"]
    else:
        preferred = ["烤腱子肉", "凤梨虾球", "蒜蓉粉丝扇贝", "特色例汤"]
    if mode == "高毛利推荐":
        preferred = [item["name"] for item in data["items"] if item["quadrant"] in {STAR, "潜力菜"}][:4]
    if mode == "招牌菜推荐":
        preferred = ["烤腱子肉", "凤梨虾球", "清蒸鲈鱼", "特色例汤"]
    names = {item["name"] for item in data["items"]}
    return [name for name in preferred if name in names][:6]


def _demo(data: dict, people: int, budget: int, scene: str, mode: str) -> dict:
    dishes = _pick_demo(data, people, budget, scene, mode)
    return {
        "dishes": dishes,
        "estimated_min": max(budget - 80, 200),
        "estimated_max": min(budget + 20, budget + 40),
        "reason": f"适合{people}人{scene}，菜品搭配丰富，预算可控，并兼顾高毛利招牌菜。",
        "script": (
            f"您{people}个人如果是{scene}，预算大概{budget}左右，"
            f"我比较推荐{'、'.join(dishes)}，吃着丰富也不会超太多。"
        ),
        "demo_fallback": True,
    }


async def recommend_dishes(
    db: Session,
    people: int,
    budget: int,
    scene: str,
    taste: str,
    first_visit: bool,
    mode: str,
) -> dict:
    data = classify_menu(db)
    compact = [
        {
            "name": item["name"],
            "price": item["price"],
            "gross_margin": item["gross_margin"],
            "quadrant": item["quadrant"],
            "sales_trend": item["sales_trend"],
        }
        for item in data["items"][:40]
    ]
    prompt = STAFF_RECOMMEND_PROMPT.format(
        people=people,
        budget=budget,
        scene=scene,
        taste=taste or "正常",
        first_visit="是" if first_visit else "否",
        mode=mode,
        menu_data=json.dumps(compact, ensure_ascii=False),
    )
    try:
        result = await generate_json(prompt)
        result["demo_fallback"] = False
    except QwenServiceError:
        result = _demo(data, people, budget, scene, mode)
    return result
