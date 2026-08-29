from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import (
    RecallAnalyzeResult,
    RecallCustomerItem,
    RecallListResponse,
    RecallMessageResult,
)
from app.services import recall_service

router = APIRouter(prefix="/api/recall", tags=["recall"])


@router.get("/customers", response_model=RecallListResponse)
def list_recall_customers(db: Session = Depends(get_db)) -> RecallListResponse:
    rows = recall_service.list_recall_customers(db)
    items = [
        RecallCustomerItem.model_validate(recall_service.serialize_recall_customer(row))
        for row in rows
    ]
    return RecallListResponse(
        total=len(items),
        high_value_sleeping_count=len(items),
        items=items,
    )


@router.post("/{customer_id}/analyze", response_model=RecallAnalyzeResult)
async def analyze_customer(customer_id: int, db: Session = Depends(get_db)) -> RecallAnalyzeResult:
    try:
        result = await recall_service.analyze_customer(db, customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RecallAnalyzeResult.model_validate(result)


@router.post("/{customer_id}/generate-message", response_model=RecallMessageResult)
async def generate_message(customer_id: int, db: Session = Depends(get_db)) -> RecallMessageResult:
    try:
        result = await recall_service.generate_recall_message(db, customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RecallMessageResult.model_validate(result)
