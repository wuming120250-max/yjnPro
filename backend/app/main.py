from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, banquet, customers, dashboard, marketing, recall, reviews
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import AiAnalysis, BanquetLead, Customer, Order, Review  # noqa: F401
from app.services.customer_service import count_customers

app = FastAPI(title="宴江南 AI 门店经营助手", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(recall.router)
app.include_router(marketing.router)
app.include_router(reviews.router)
app.include_router(banquet.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    from scripts.seed_db import seed_if_empty

    db = SessionLocal()
    try:
        if count_customers(db) == 0:
            seed_if_empty(db)
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
