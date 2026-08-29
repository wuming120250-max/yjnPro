from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas import LoginRequest, LoginResponse, SettingsResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    settings = get_settings()
    if payload.username != settings.admin_username or payload.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="账号或密码错误")
    token = create_access_token(payload.username)
    return LoginResponse(
        token=token,
        username=payload.username,
        store_name=settings.store_name,
    )


@router.get("/settings", response_model=SettingsResponse)
def get_app_settings() -> SettingsResponse:
    settings = get_settings()
    return SettingsResponse(
        store_name=settings.store_name,
        demo_mode=settings.demo_mode or not bool(settings.qwen_api_key),
        ai_configured=bool(settings.qwen_api_key) and not settings.demo_mode,
        username=settings.admin_username,
    )
