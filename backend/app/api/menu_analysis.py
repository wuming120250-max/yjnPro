from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import menu_ai_service, menu_service

router = APIRouter(prefix="/api/menu-analysis", tags=["menu-analysis"])


@router.get("")
def menu_analysis(db: Session = Depends(get_db)) -> dict:
    return menu_service.classify_menu(db)


@router.post("/diagnose")
async def diagnose(db: Session = Depends(get_db)) -> dict:
    return await menu_ai_service.diagnose_menu(db)
