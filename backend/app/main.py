from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    banquet,
    customers,
    daily_report,
    dashboard,
    marketing,
    menu_analysis,
    recall,
    revenue,
    reviews,
    staff,
    table_efficiency,
)
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import (  # noqa: F401
    AiAnalysis,
    AiDailyReport,
    BanquetLead,
    Customer,
    DailyRevenue,
    MenuItem,
    Order,
    Review,
    TableOrder,
)
from app.services.customer_service import count_customers

app = FastAPI(title="宴江南 AI 老板经营诊断系统", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(daily_report.router)
app.include_router(menu_analysis.router)
app.include_router(revenue.router)
app.include_router(table_efficiency.router)
app.include_router(staff.router)
app.include_router(customers.router)
app.include_router(recall.router)
app.include_router(marketing.router)
app.include_router(reviews.router)
app.include_router(banquet.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    from scripts.seed_db import seed_if_empty, seed_v2_if_empty

    db = SessionLocal()
    try:
        if count_customers(db) == 0:
            seed_if_empty(db)
        seed_v2_if_empty(db)
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
