from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.core.prompts import MARKETING_PROMPT
from app.models.ai_analysis import AiAnalysis
from app.services.qwen_service import QwenServiceError, generate_json


def _demo_plan(goal: str, dish: str, promotion: str, target_customer: str, date_range: str) -> dict[str, Any]:
    theme = "周末一家人，来宴江南吃顿好饭" if "家庭" in goal else f"{goal}，就来宴江南"
    audience = target_customer or ("25～45岁家庭客户" if "家庭" in goal else "门店周边老客户与新客")
    when = date_range or "本周末"
    return {
        "theme": theme,
        "target_customer": audience,
        "strategy": (
            f"围绕「{goal}」场景，强调菜品丰富、环境舒适、适合多人聚餐。"
            f"主推{dish}，用「{promotion}」降低决策成本，引导客户把宴江南作为{when}的首选。"
        ),
        "activity_suggestion": (
            f"在门口和包间摆放{goal}主题立牌，服务员主动介绍{dish}；"
            "老客户微信一对一触达，朋友圈与点评同步露出优惠。"
        ),
        "moments_copy": (
            f"周末不知道吃什么？\n\n一家人难得聚在一起，不如来宴江南吃顿热乎乎的饭。\n\n"
            f"本周{goal}主推{dish}，{promotion}。\n适合4～6人小聚，包间也可提前预约。"
        ),
        "wechat_group_copy": (
            f"各位老板注意啦～{when}宴江南{goal}活动开始了。\n"
            f"主打{dish}，{promotion}。家庭、朋友小聚都很合适，需要订座直接群里说。"
        ),
        "staff_script": (
            f"您好，我们这周主推{goal}，招牌是{dish}。"
            f"现在到店{promotion}，很适合您今天这一桌，需要我帮您推荐一套吗？"
        ),
        "dianping_copy": (
            f"青岛城阳宴江南汇海路店｜{when}{goal}推荐。\n"
            f"主打{dish}，环境安静适合聚餐。到店{promotion}，欢迎提前订座。"
        ),
        "demo_fallback": True,
    }


async def generate_marketing_plan(
    db: Session,
    goal: str,
    dish: str,
    promotion: str,
    target_customer: str,
    date_range: str,
) -> dict[str, Any]:
    prompt = MARKETING_PROMPT.format(
        goal=goal,
        dish=dish,
        promotion=promotion,
        target_customer=target_customer or "未指定",
        date_range=date_range or "近期",
    )
    try:
        result = await generate_json(prompt)
        result["demo_fallback"] = False
    except QwenServiceError:
        result = _demo_plan(goal, dish, promotion, target_customer, date_range)
    record = AiAnalysis(
        analysis_type="marketing",
        target_id=goal,
        input_data=json.dumps(
            {
                "goal": goal,
                "dish": dish,
                "promotion": promotion,
                "target_customer": target_customer,
                "date_range": date_range,
            },
            ensure_ascii=False,
        ),
        result=json.dumps(result, ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    return result
