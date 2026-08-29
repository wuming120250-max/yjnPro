from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.core.prompts import RECALL_ANALYZE_PROMPT, RECALL_MESSAGE_PROMPT
from app.models.ai_analysis import AiAnalysis
from app.models.customer import Customer
from app.services.customer_service import (
    LEVEL_HIGH_SLEEP,
    compute_customer_level,
    current_biz_date,
    get_customer,
    get_order_types,
    list_customers,
    serialize_customer,
    sleep_days,
)
from app.services.qwen_service import QwenServiceError, generate_json, generate_text


def _recall_priority(sleep: int, total_amount: float, total_orders: int) -> int:
    score = 3
    if sleep >= 90:
        score += 1
    if sleep >= 75:
        score += 1
    if float(total_amount) >= 4000 or total_orders >= 9:
        score += 1
    return min(score, 5)


def list_recall_customers(db: Session) -> list[Customer]:
    _, rows = list_customers(db, page=1, page_size=10000)
    today = current_biz_date()
    recall_rows = [
        row
        for row in rows
        if compute_customer_level(
            float(row.total_amount), row.total_orders, row.last_order_date, today
        )
        == LEVEL_HIGH_SLEEP
    ]
    recall_rows.sort(
        key=lambda row: (
            sleep_days(row.last_order_date, today),
            float(row.total_amount),
        ),
        reverse=True,
    )
    return recall_rows


def serialize_recall_customer(customer: Customer) -> dict[str, Any]:
    data = serialize_customer(customer)
    priority = _recall_priority(
        data["sleep_days"], data["total_amount"], data["total_orders"]
    )
    data["recall_priority"] = priority
    data["recall_priority_label"] = "★" * priority
    return data


def _demo_analyze(customer: Customer, order_types: list[str]) -> dict[str, Any]:
    days = sleep_days(customer.last_order_date)
    amount = float(customer.total_amount)
    score = _recall_priority(days, amount, customer.total_orders)
    tags = customer.tags or "老客户"
    scene = order_types[0] if order_types else (tags.split(",")[0] if tags else "到店用餐")
    return {
        "customer_value": "★" * score,
        "customer_value_score": score,
        "customer_status": "高价值沉睡客户",
        "churn_risk": "高" if days >= 75 else "中",
        "judgment": (
            f"{customer.customer_name}历史消费频率较高，累计到店 {customer.total_orders} 次，"
            f"累计消费 {amount:.0f} 元，平均客单 {float(customer.average_order_amount):.0f} 元，"
            f"但已经 {days} 天未到店。属于重点召回客户。"
        ),
        "recall_suggestion": (
            f"建议本周内通过微信进行一次老客户关怀召回，可结合「{scene}」场景给出到店理由，"
            "避免强推销，先关心再邀约。"
        ),
        "recommended_channel": "微信一对一沟通",
        "recommended_offer": f"针对{scene}的到店优惠或预留安静座位",
        "demo_fallback": True,
    }


def _demo_message(customer: Customer, order_types: list[str]) -> str:
    name = customer.customer_name
    honorific = "姐" if "女" in name or customer.gender == "女" else "哥"
    short = name.replace("女士", "").replace("先生", "")
    scene = "家庭聚餐" if "家庭" in (customer.tags or "") else (
        "商务宴请" if "商务" in (customer.tags or "") else (order_types[0] if order_types else "到店吃饭")
    )
    if short == "赵":
        return (
            "赵姐您好，好久没见啦。之前您带家人来店里吃饭，家里人都挺喜欢我们家海鲜的。"
            "这周店里上了几道新的特色菜，也有家庭聚餐的优惠，您要是方便，欢迎随时过来坐坐，我们给您留个安静的位置。"
        )
    if short == "张" and customer.gender == "男":
        return (
            "张先生您好，好久没联系了。上次您来宴江南招待客人，我们一直记着。"
            "最近店里包间档期还比较宽裕，如果后面有宴请或同事聚餐，欢迎随时跟我说，我帮您先看位置。"
        )
    return (
        f"{short}{honorific}您好，好久没见啦。之前您来宴江南{scene}，给我们留下的印象很深。"
        "这周店里有几道新菜，也有老客户小优惠，您方便的时候过来坐坐，我们给您留位置。"
    )


def _save_analysis(db: Session, analysis_type: str, target_id: str, input_data: dict, result: dict) -> None:
    record = AiAnalysis(
        analysis_type=analysis_type,
        target_id=target_id,
        input_data=json.dumps(input_data, ensure_ascii=False, default=str),
        result=json.dumps(result, ensure_ascii=False),
    )
    db.add(record)
    db.commit()


async def analyze_customer(db: Session, customer_id: int) -> dict[str, Any]:
    customer = get_customer(db, customer_id)
    if customer is None:
        raise ValueError("客户不存在")
    order_types = get_order_types(db, customer_id)
    prompt = RECALL_ANALYZE_PROMPT.format(
        customer_name=customer.customer_name,
        total_orders=customer.total_orders,
        total_amount=float(customer.total_amount),
        last_order_date=customer.last_order_date,
        average_order_amount=float(customer.average_order_amount),
        order_types="、".join(order_types) or "普通用餐",
        tags=customer.tags or "无",
        sleep_days=sleep_days(customer.last_order_date),
    )
    try:
        result = await generate_json(prompt)
        result["demo_fallback"] = False
    except QwenServiceError:
        result = _demo_analyze(customer, order_types)
    _save_analysis(
        db,
        "customer_recall",
        str(customer_id),
        {"prompt": prompt},
        result,
    )
    return result


async def generate_recall_message(db: Session, customer_id: int) -> dict[str, Any]:
    customer = get_customer(db, customer_id)
    if customer is None:
        raise ValueError("客户不存在")
    order_types = get_order_types(db, customer_id)
    prompt = RECALL_MESSAGE_PROMPT.format(
        customer_name=customer.customer_name,
        total_orders=customer.total_orders,
        total_amount=float(customer.total_amount),
        last_order_date=customer.last_order_date,
        tags=customer.tags or "无",
        order_types="、".join(order_types) or "普通用餐",
    )
    try:
        message = await generate_text(prompt)
        fallback = False
    except QwenServiceError:
        message = _demo_message(customer, order_types)
        fallback = True
    result = {"message": message, "demo_fallback": fallback}
    _save_analysis(db, "customer_recall", f"{customer_id}-message", {"prompt": prompt}, result)
    return result
