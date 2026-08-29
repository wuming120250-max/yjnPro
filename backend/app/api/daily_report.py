from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import daily_report_service

router = APIRouter(prefix="/api/daily-report", tags=["daily-report"])


@router.get("")
def get_daily_report(db: Session = Depends(get_db)) -> dict:
    return daily_report_service.get_daily_report(db)


@router.post("/generate")
async def generate_daily_report(db: Session = Depends(get_db)) -> dict:
    return await daily_report_service.generate_daily_report(db)
