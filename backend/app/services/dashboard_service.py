from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.banquet_lead import BanquetLead
from app.models.customer import Customer
from app.models.daily_revenue import DailyRevenue
from app.services.customer_service import compute_customer_level, current_biz_date
from app.services.daily_report_service import build_scorecard, diagnosis_items
from app.services.opportunities.opportunity_service import top_opportunities
from app.services.recall_service import list_recall_customers


def get_overview(db: Session) -> dict:
    today = current_biz_date()
    card = build_scorecard(db)
    diagnosis = diagnosis_items(card)

    customer_count = db.scalar(select(func.count(Customer.id))) or 0
    old_customers = (
        db.scalar(select(func.count(Customer.id)).where(Customer.total_orders >= 2)) or 0
    )
    old_customer_rate = round(old_customers / customer_count * 100, 0) if customer_count else 0
    recall_customers = list_recall_customers(db)
    banquet_pending = (
        db.scalar(
            select(func.count(BanquetLead.id)).where(BanquetLead.status.in_(["待跟进", "已联系"]))
        )
        or 0
    )

    trend_rows = list(
        db.scalars(
            select(DailyRevenue)
            .where(DailyRevenue.date >= today - timedelta(days=6))
            .order_by(DailyRevenue.date.asc())
        ).all()
    )
    trend = [
        {"date": row.date.isoformat(), "revenue": float(row.revenue), "orders": row.order_count}
        for row in trend_rows
    ]

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
        "today_revenue": card["today_revenue"],
        "today_orders": card["today_orders"],
        "average_order_amount": card["average_order_amount"],
        "forecast_revenue": card["forecast_revenue"],
        "revenue_change": card["revenue_change"],
        "order_change": card["order_change"],
        "aov_change": card["aov_change"],
        "week_change": card["week_change"],
        "score": card["score"],
        "stars_label": card["stars_label"],
        "recommendation": "重点推广家庭聚餐套餐",
        "diagnosis": diagnosis,
        "menu_counts": card["menu_counts"],
        "customer_count": customer_count,
        "old_customer_rate": old_customer_rate,
        "pending_followups": len(recall_customers) + banquet_pending,
        "high_value_sleeping_count": len(recall_customers),
        "banquet_pending_count": banquet_pending,
        "insights": [
            {
                "level": item["level"],
                "title": item["title"],
                "suggestion": item["suggestion"],
            }
            for item in diagnosis
        ],
        "trend": trend,
        "level_distribution": distribution,
        "top_opportunities": top_opportunities(db, 3),
    }
