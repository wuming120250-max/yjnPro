from datetime import date
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.customer import Customer
from app.models.order import Order

TODAY = date(2026, 8, 29)

LEVEL_HIGH_VALUE = "高价值客户"
LEVEL_SLEEPING = "沉睡客户"
LEVEL_HIGH_SLEEP = "高价值沉睡客户"
LEVEL_POTENTIAL = "潜力客户"
LEVEL_NORMAL = "普通客户"


def current_biz_date() -> date:
    return date.today() if date.today().year >= 2026 else TODAY


def sleep_days(last_order_date: date | None, today: date | None = None) -> int:
    if last_order_date is None:
        return 999
    return ((today or current_biz_date()) - last_order_date).days


def compute_customer_level(
    total_amount: float,
    total_orders: int,
    last_order_date: date | None,
    today: date | None = None,
) -> str:
    days = sleep_days(last_order_date, today)
    high_value = float(total_amount) >= 2000 or total_orders >= 5
    sleeping = days >= 60
    if high_value and sleeping:
        return LEVEL_HIGH_SLEEP
    if sleeping:
        return LEVEL_SLEEPING
    if high_value:
        return LEVEL_HIGH_VALUE
    if total_orders >= 2 or float(total_amount) >= 800:
        return LEVEL_POTENTIAL
    return LEVEL_NORMAL


def split_tags(tags: str | None) -> list[str]:
    if not tags:
        return []
    return [item.strip() for item in tags.replace("，", ",").split(",") if item.strip()]


def serialize_customer(customer: Customer, today: date | None = None) -> dict[str, Any]:
    days = sleep_days(customer.last_order_date, today)
    return {
        "id": customer.id,
        "customer_name": customer.customer_name,
        "phone": customer.phone,
        "gender": customer.gender,
        "age": customer.age,
        "customer_level": compute_customer_level(
            float(customer.total_amount),
            customer.total_orders,
            customer.last_order_date,
            today,
        ),
        "total_orders": customer.total_orders,
        "total_amount": float(customer.total_amount),
        "last_order_date": customer.last_order_date,
        "average_order_amount": float(customer.average_order_amount),
        "birthday": customer.birthday,
        "tags": customer.tags,
        "tag_list": split_tags(customer.tags),
        "sleep_days": days,
    }


def list_customers(
    db: Session,
    keyword: str | None = None,
    level: str | None = None,
    tag: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[int, list[Customer]]:
    stmt = select(Customer)
    if keyword:
        like = f"%{keyword.strip()}%"
        stmt = stmt.where(
            or_(Customer.customer_name.ilike(like), Customer.phone.ilike(like))
        )
    if tag:
        stmt = stmt.where(Customer.tags.ilike(f"%{tag}%"))

    rows = list(db.scalars(stmt.order_by(Customer.total_amount.desc())).all())
    today = current_biz_date()
    if level:
        rows = [
            row
            for row in rows
            if compute_customer_level(
                float(row.total_amount), row.total_orders, row.last_order_date, today
            )
            == level
        ]
    total = len(rows)
    start = (page - 1) * page_size
    return total, rows[start : start + page_size]


def get_customer(db: Session, customer_id: int) -> Customer | None:
    return db.get(Customer, customer_id)


def get_customer_detail(db: Session, customer_id: int) -> Customer | None:
    stmt = (
        select(Customer)
        .options(selectinload(Customer.orders))
        .where(Customer.id == customer_id)
    )
    return db.scalars(stmt).first()


def get_order_types(db: Session, customer_id: int) -> list[str]:
    rows = db.scalars(
        select(Order.order_type)
        .where(Order.customer_id == customer_id)
        .distinct()
    ).all()
    return list(rows)


def count_customers(db: Session) -> int:
    return db.scalar(select(func.count(Customer.id))) or 0
