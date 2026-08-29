from __future__ import annotations

from datetime import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.table_order import TableOrder
from app.services.customer_service import current_biz_date

SLOTS = [
    ("11:00～12:00", 11),
    ("12:00～13:00", 12),
    ("13:00～14:00", 13),
    ("17:00～18:00", 17),
    ("18:00～19:00", 18),
    ("19:00～20:00", 19),
    ("20:00～21:00", 20),
]
NORMAL_DURATION = 72
PEAK_HOUR = 18


def _hour(value: time) -> int:
    return value.hour


def list_slots(db: Session, day=None) -> list[dict]:
    day = day or current_biz_date()
    rows = list(db.scalars(select(TableOrder).where(TableOrder.order_date == day)).all())
    result = []
    for label, hour in SLOTS:
        bucket = [row for row in rows if _hour(row.start_time) == hour]
        if not bucket:
            result.append(
                {
                    "label": label,
                    "hour": hour,
                    "table_count": 0,
                    "avg_duration": 0,
                    "turnover": 0,
                    "revenue": 0,
                    "is_abnormal": False,
                }
            )
            continue
        avg_duration = round(sum(row.duration_minutes for row in bucket) / len(bucket))
        result.append(
            {
                "label": label,
                "hour": hour,
                "table_count": len({row.table_name for row in bucket}),
                "avg_duration": avg_duration,
                "turnover": len(bucket),
                "revenue": round(sum(float(row.amount) for row in bucket), 0),
                "is_abnormal": hour == PEAK_HOUR and avg_duration >= 90,
            }
        )
    return result


def peak_slot_summary(db: Session, day=None) -> dict:
    slots = list_slots(db, day)
    peak = next((item for item in slots if item["hour"] == PEAK_HOUR), None)
    if peak is None:
        return {
            "label": "18:00～19:00",
            "avg_duration": 0,
            "normal_duration": NORMAL_DURATION,
            "is_abnormal": False,
            "table_count": 0,
            "utilization": 0,
        }
    return {
        "label": "18:30～19:30" if peak["is_abnormal"] else peak["label"],
        "avg_duration": peak["avg_duration"],
        "normal_duration": NORMAL_DURATION,
        "is_abnormal": peak["is_abnormal"],
        "table_count": peak["table_count"],
        "utilization": min(100, peak["table_count"] * 7),
        "revenue": peak["revenue"],
    }
