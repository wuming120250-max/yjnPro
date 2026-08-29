from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import table_ai_service

router = APIRouter(prefix="/api/table-efficiency", tags=["table-efficiency"])


@router.get("")
def table_efficiency(db: Session = Depends(get_db)) -> dict:
    return table_ai_service.get_table_efficiency(db)


@router.post("/analyze")
async def analyze(db: Session = Depends(get_db)) -> dict:
    return await table_ai_service.analyze_table_efficiency(db)
