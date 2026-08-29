from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import (
    BanquetAnalyzeResult,
    BanquetLeadCreate,
    BanquetLeadItem,
    BanquetLeadListResponse,
    BanquetLeadUpdate,
)
from app.services import banquet_service

router = APIRouter(prefix="/api/banquet-leads", tags=["banquet"])


@router.get("", response_model=BanquetLeadListResponse)
def list_leads(
    status: str | None = Query(default=None), db: Session = Depends(get_db)
) -> BanquetLeadListResponse:
    items = [
        BanquetLeadItem.model_validate(item) for item in banquet_service.list_leads(db, status)
    ]
    return BanquetLeadListResponse(total=len(items), items=items)


@router.post("", response_model=BanquetLeadItem)
def create_lead(payload: BanquetLeadCreate, db: Session = Depends(get_db)) -> BanquetLeadItem:
    lead = banquet_service.create_lead(db, payload.model_dump())
    return BanquetLeadItem.model_validate(lead)


@router.patch("/{lead_id}", response_model=BanquetLeadItem)
def update_lead(
    lead_id: int, payload: BanquetLeadUpdate, db: Session = Depends(get_db)
) -> BanquetLeadItem:
    lead = banquet_service.update_lead(db, lead_id, payload.model_dump(exclude_unset=True))
    if lead is None:
        raise HTTPException(status_code=404, detail="线索不存在")
    return BanquetLeadItem.model_validate(lead)


@router.post("/{lead_id}/analyze", response_model=BanquetAnalyzeResult)
async def analyze_lead(lead_id: int, db: Session = Depends(get_db)) -> BanquetAnalyzeResult:
    try:
        result = await banquet_service.analyze_lead(db, lead_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return BanquetAnalyzeResult.model_validate(result)
