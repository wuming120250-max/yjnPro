from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.banquet_lead import BanquetLead
from app.models.customer import Customer
from app.models.order import Order
from app.services.customer_service import (
    LEVEL_HIGH_SLEEP,
    compute_customer_level,
    current_biz_date,
)
from app.services.recall_service import list_recall_customers


def get_overview(db: Session) -> dict:
    today = current_biz_date()
    today_revenue = db.scalar(
        select(func.coalesce(func.sum(Order.amount), 0)).where(Order.order_date == today)
    )
    today_orders = db.scalar(select(func.count(Order.id)).where(Order.order_date == today)) or 0
    today_revenue_value = float(today_revenue or 0)
    average_order_amount = round(today_revenue_value / today_orders, 0) if today_orders else 0
    customer_count = db.scalar(select(func.count(Customer.id))) or 0
    old_customers = (
        db.scalar(select(func.count(Customer.id)).where(Customer.total_orders >= 2)) or 0
    )
    old_customer_rate = round(old_customers / customer_count * 100, 0) if customer_count else 0

    recall_customers = list_recall_customers(db)
    banquet_pending = (
        db.scalar(
            select(func.count(BanquetLead.id)).where(
                BanquetLead.status.in_(["待跟进", "已联系"])
            )
        )
        or 0
    )
    pending_followups = len(recall_customers) + banquet_pending

    insights = [
        {
            "level": "warning",
            "title": f"{len(recall_customers)}名高价值客户超过60天未消费",
            "suggestion": "建议进行老客户召回。",
        },
        {
            "level": "warning",
            "title": "最近评价中「家庭聚餐」出现频率较高",
            "suggestion": "建议设计家庭聚餐套餐。",
        },
        {
            "level": "success",
            "title": "近期宴请客户线索增加",
            "suggestion": "建议重点跟进25人以上聚餐客户。",
        },
    ]

    trend = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        revenue = db.scalar(
            select(func.coalesce(func.sum(Order.amount), 0)).where(Order.order_date == day)
        )
        orders = db.scalar(select(func.count(Order.id)).where(Order.order_date == day)) or 0
        trend.append(
            {
                "date": day.isoformat(),
                "revenue": float(revenue or 0),
                "orders": orders,
            }
        )

    customers = list(db.scalars(select(Customer)).all())
    distribution: dict[str, int] = {}
    for customer in customers:
        level = compute_customer_level(
            float(customer.total_amount),
            customer.total_orders,
            customer.last_order_date,
            today,
        )
        distribution[level] = distribution.get(level, 0) + 1

    return {
        "today_revenue": today_revenue_value,
        "today_orders": today_orders,
        "average_order_amount": average_order_amount,
        "customer_count": customer_count,
        "old_customer_rate": old_customer_rate,
        "pending_followups": pending_followups,
        "high_value_sleeping_count": len(recall_customers),
        "banquet_pending_count": banquet_pending,
        "insights": insights,
        "trend": trend,
        "level_distribution": distribution,
    }
