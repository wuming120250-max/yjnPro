from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    order_no: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    order_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    people_count: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    order_type: Mapped[str] = mapped_column(String(30), nullable=False)
    table_type: Mapped[str] = mapped_column(String(30), nullable=False, default="大厅")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    customer: Mapped["Customer"] = relationship(back_populates="orders")  # noqa: F821
