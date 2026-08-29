from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DailyRevenue(Base):
    __tablename__ = "daily_revenue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True, index=True)
    revenue: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    average_order_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    lunch_revenue: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    dinner_revenue: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    banquet_revenue: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    lunch_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dinner_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    family_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
