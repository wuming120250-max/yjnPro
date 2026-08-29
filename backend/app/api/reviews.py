from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import ReviewAnalyzeResult, ReviewItem, ReviewListResponse
from app.services import review_service

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("", response_model=ReviewListResponse)
def list_reviews(
    sentiment: str | None = Query(default=None),
    source: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ReviewListResponse:
    stats = review_service.review_stats(db)
    items = [
        ReviewItem.model_validate(item)
        for item in review_service.list_reviews(db, sentiment=sentiment, source=source)
    ]
    return ReviewListResponse(
        total=stats["total"],
        average_rating=stats["average_rating"],
        positive_rate=stats["positive_rate"],
        negative_rate=stats["negative_rate"],
        items=items,
    )


@router.post("/analyze", response_model=ReviewAnalyzeResult)
async def analyze_reviews(db: Session = Depends(get_db)) -> ReviewAnalyzeResult:
    result = await review_service.analyze_reviews(db)
    return ReviewAnalyzeResult.model_validate(result)
