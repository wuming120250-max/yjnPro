from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import MarketingGenerateRequest, MarketingPlan
from app.services import marketing_service

router = APIRouter(prefix="/api/marketing", tags=["marketing"])


@router.post("/generate", response_model=MarketingPlan)
async def generate_plan(
    payload: MarketingGenerateRequest, db: Session = Depends(get_db)
) -> MarketingPlan:
    result = await marketing_service.generate_marketing_plan(
        db,
        goal=payload.goal,
        dish=payload.dish,
        promotion=payload.promotion,
        target_customer=payload.target_customer,
        date_range=payload.date_range,
    )
    return MarketingPlan.model_validate(result)
