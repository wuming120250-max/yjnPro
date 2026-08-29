from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.models.banquet_lead import BanquetLead  # noqa: E402
from app.models.customer import Customer  # noqa: E402
from app.models.daily_revenue import DailyRevenue  # noqa: E402
from app.models.menu_item import MenuItem  # noqa: E402
from app.models.order import Order  # noqa: E402
from app.models.review import Review  # noqa: E402
from app.models.table_order import TableOrder  # noqa: E402
from scripts.generate_demo_data import demo_dir, generate_all  # noqa: E402
from scripts.generate_v2_demo_data import generate_v2  # noqa: E402


def _parse_date(value: str):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def seed_if_empty(db: Session) -> None:
    data_dir = demo_dir()
    required = ["customers.csv", "orders.csv", "reviews.csv", "banquet_leads.csv"]
    if not all((data_dir / name).exists() for name in required):
        generate_all(data_dir)

    customers_rows = _read(data_dir / "customers.csv")
    orders_rows = _read(data_dir / "orders.csv")
    reviews_rows = _read(data_dir / "reviews.csv")
    leads_rows = _read(data_dir / "banquet_leads.csv")

    customer_map: dict[int, Customer] = {}
    for index, row in enumerate(customers_rows, start=1):
        customer = Customer(
            customer_name=row["customer_name"],
            phone=row["phone"],
            gender=row["gender"],
            age=int(row["age"]) if row.get("age") else None,
            customer_level=row["customer_level"],
            total_orders=int(float(row["total_orders"])),
            total_amount=float(row["total_amount"]),
            last_order_date=_parse_date(row["last_order_date"]),
            average_order_amount=float(row["average_order_amount"]),
            birthday=_parse_date(row.get("birthday") or ""),
            tags=row.get("tags") or "",
        )
        db.add(customer)
        db.flush()
        customer_map[index] = customer

    for row in orders_rows:
        customer = customer_map[int(row["customer_index"])]
        db.add(
            Order(
                customer_id=customer.id,
                order_no=row["order_no"],
                order_date=_parse_date(row["order_date"]),
                amount=float(row["amount"]),
                people_count=int(row["people_count"]),
                order_type=row["order_type"],
                table_type=row["table_type"],
            )
        )

    for row in reviews_rows:
        db.add(
            Review(
                customer_name=row["customer_name"],
                rating=int(row["rating"]),
                content=row["content"],
                review_date=_parse_date(row["review_date"]),
                source=row["source"],
                tags=row.get("tags") or "",
                sentiment=row["sentiment"],
            )
        )

    for row in leads_rows:
        db.add(
            BanquetLead(
                customer_name=row["customer_name"],
                phone=row["phone"],
                event_type=row["event_type"],
                people_count=int(row["people_count"]),
                expected_amount=row["expected_amount"],
                event_date=_parse_date(row.get("event_date") or ""),
                source=row["source"],
                status=row["status"],
                notes=row.get("notes") or "",
            )
        )
    db.commit()


def _parse_time(value: str):
    if not value:
        return None
    parts = value.split(":")
    return datetime.strptime(":".join(parts[:3]) if len(parts) >= 2 else value, "%H:%M:%S" if len(parts) >= 3 else "%H:%M").time()


def seed_v2_if_empty(db: Session) -> None:
    existing = db.scalar(select(func.count(MenuItem.id))) or 0
    if existing:
        return
    data_dir = demo_dir()
    required = ["menu_items.csv", "daily_revenue.csv", "table_orders.csv"]
    if not all((data_dir / name).exists() for name in required):
        generate_v2(data_dir)

    for row in _read(data_dir / "menu_items.csv"):
        db.add(
            MenuItem(
                name=row["name"],
                category=row["category"],
                price=float(row["price"]),
                cost_price=float(row["cost_price"]),
                gross_profit=float(row["gross_profit"]),
                gross_margin=float(row["gross_margin"]),
                sales_count=int(float(row["sales_count"])),
                sales_amount=float(row["sales_amount"]),
                sales_trend=float(row["sales_trend"]),
                status=row.get("status") or "active",
            )
        )
    for row in _read(data_dir / "daily_revenue.csv"):
        db.add(
            DailyRevenue(
                date=_parse_date(row["date"]),
                revenue=float(row["revenue"]),
                order_count=int(row["order_count"]),
                average_order_amount=float(row["average_order_amount"]),
                lunch_revenue=float(row["lunch_revenue"]),
                dinner_revenue=float(row["dinner_revenue"]),
                banquet_revenue=float(row["banquet_revenue"]),
                lunch_orders=int(row.get("lunch_orders") or 0),
                dinner_orders=int(row.get("dinner_orders") or 0),
                family_orders=int(row.get("family_orders") or 0),
            )
        )
    for row in _read(data_dir / "table_orders.csv"):
        db.add(
            TableOrder(
                table_name=row["table_name"],
                seats=int(row["seats"]),
                order_date=_parse_date(row["order_date"]),
                start_time=_parse_time(row["start_time"]),
                end_time=_parse_time(row["end_time"]),
                duration_minutes=int(row["duration_minutes"]),
                amount=float(row["amount"]),
                order_type=row.get("order_type") or "普通用餐",
            )
        )
    db.commit()


def main() -> None:
    from app.db.base import Base
    from app.db.session import SessionLocal, engine
    from app.services.customer_service import count_customers

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if count_customers(db) == 0:
            seed_if_empty(db)
            print("v1 seed completed")
        else:
            print("database already has customers, skip v1 seed")
        seed_v2_if_empty(db)
        print("v2 seed completed")
    finally:
        db.close()


if __name__ == "__main__":
    main()
