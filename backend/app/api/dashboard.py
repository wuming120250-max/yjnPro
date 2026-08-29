from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import DashboardOverviewResponse
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def overview(db: Session = Depends(get_db)) -> DashboardOverviewResponse:
    return DashboardOverviewResponse.model_validate(dashboard_service.get_overview(db))
