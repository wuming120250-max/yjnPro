from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem

STAR = "明星菜"
POTENTIAL = "潜力菜"
TRAFFIC = "引流菜"
ELIMINATE = "淘汰候选"

ADVICE = {
    STAR: "重点推广。",
    POTENTIAL: "让服务员重点推荐。",
    TRAFFIC: "控制成本，不宜过度依赖。",
    ELIMINATE: "考虑优化、换菜或者调整价格。",
}


def serialize_dish(item: MenuItem, avg_sales: float, avg_margin: float) -> dict[str, Any]:
    sales = item.sales_count
    margin = float(item.gross_margin)
    if sales > avg_sales and margin > avg_margin:
        quadrant = STAR
    elif sales <= avg_sales and margin > avg_margin:
        quadrant = POTENTIAL
    elif sales > avg_sales and margin <= avg_margin:
        quadrant = TRAFFIC
    else:
        quadrant = ELIMINATE
    return {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "price": float(item.price),
        "cost_price": float(item.cost_price),
        "gross_profit": float(item.gross_profit),
        "gross_margin": round(margin, 1),
        "sales_count": sales,
        "sales_amount": float(item.sales_amount),
        "sales_trend": float(item.sales_trend),
        "status": item.status,
        "quadrant": quadrant,
        "advice": ADVICE[quadrant],
    }


def list_active_dishes(db: Session) -> list[MenuItem]:
    return list(
        db.scalars(
            select(MenuItem).where(MenuItem.status == "active").order_by(MenuItem.sales_amount.desc())
        ).all()
    )


def classify_menu(db: Session) -> dict[str, Any]:
    items = list_active_dishes(db)
    if not items:
        return {
            "avg_sales": 0,
            "avg_margin": 0,
            "items": [],
            "counts": {STAR: 0, POTENTIAL: 0, TRAFFIC: 0, ELIMINATE: 0},
        }
    avg_sales = sum(item.sales_count for item in items) / len(items)
    avg_margin = sum(float(item.gross_margin) for item in items) / len(items)
    serialized = [serialize_dish(item, avg_sales, avg_margin) for item in items]
    counts = {STAR: 0, POTENTIAL: 0, TRAFFIC: 0, ELIMINATE: 0}
    for row in serialized:
        counts[row["quadrant"]] += 1
    return {
        "avg_sales": round(avg_sales, 1),
        "avg_margin": round(avg_margin, 1),
        "items": serialized,
        "counts": counts,
    }
