from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.opportunities import opportunity_service

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


@router.get("")
def list_opportunities(
    type: str | None = None,
    level: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    return opportunity_service.list_opportunities(
        db, type=type, level=level, status=status, page=page, page_size=page_size
    )


@router.get("/today-priority")
def today_priority(db: Session = Depends(get_db)) -> dict:
    item = opportunity_service.today_focus(db)
    if item is None:
        return {"item": None}
    return {"item": opportunity_service.serialize_opportunity(item)}


@router.post("/generate")
async def generate(force: bool = False, db: Session = Depends(get_db)) -> dict:
    return await opportunity_service.generate_opportunities(db, force=force)


@router.get("/{opp_id}")
def get_opportunity(opp_id: int, db: Session = Depends(get_db)) -> dict:
    item = opportunity_service.get_opportunity(db, opp_id)
    if item is None:
        raise HTTPException(status_code=404, detail="机会不存在")
    return opportunity_service.serialize_opportunity(item)


@router.post("/{opp_id}/analyze")
async def analyze(opp_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        return await opportunity_service.analyze_opportunity(db, opp_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{opp_id}/processing")
def processing(opp_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        return opportunity_service.set_processing(db, opp_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{opp_id}/complete")
def complete(opp_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        return opportunity_service.complete_opportunity(db, opp_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{opp_id}/ignore")
def ignore(opp_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        return opportunity_service.ignore_opportunity(db, opp_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
