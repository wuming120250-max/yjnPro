from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import revenue_service

router = APIRouter(prefix="/api/revenue-analysis", tags=["revenue-analysis"])


@router.get("")
def revenue_analysis(days: int = Query(default=30, ge=7, le=30), db: Session = Depends(get_db)) -> dict:
    return revenue_service.detect_anomaly(db)


@router.post("/analyze")
async def analyze_revenue(db: Session = Depends(get_db)) -> dict:
    return await revenue_service.analyze_revenue(db)
