from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import staff_service

router = APIRouter(prefix="/api/staff-assistant", tags=["staff-assistant"])


class RecommendRequest(BaseModel):
    people: int = Field(ge=1, le=30)
    budget: int = Field(ge=50)
    scene: str = "家庭聚餐"
    taste: str = "正常"
    first_visit: bool = True
    mode: str = "普通推荐"


@router.post("/recommend")
async def recommend(payload: RecommendRequest, db: Session = Depends(get_db)) -> dict:
    return await staff_service.recommend_dishes(
        db,
        people=payload.people,
        budget=payload.budget,
        scene=payload.scene,
        taste=payload.taste,
        first_visit=payload.first_visit,
        mode=payload.mode,
    )
