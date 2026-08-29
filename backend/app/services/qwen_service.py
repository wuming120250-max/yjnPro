from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class QwenServiceError(Exception):
    pass


def _extract_json(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            return None
    return None


def _is_real_ai_enabled() -> bool:
    settings = get_settings()
    return bool(settings.qwen_api_key) and not settings.demo_mode


async def generate_text(prompt: str, *, json_mode: bool = False) -> str:
    """Unified Qwen text generation via DashScope compatible-mode API."""
    settings = get_settings()
    if not _is_real_ai_enabled():
        raise QwenServiceError("DEMO_MODE")

    url = settings.qwen_api_base.rstrip("/") + "/chat/completions"
    system_content = (
        "你是宴江南门店的专业经营顾问。只返回合法 JSON 对象，不要 markdown，不要多余说明。"
        if json_mode
        else "你是宴江南门店的专业经营顾问，回答简洁、可执行、使用中文。"
    )
    payload: dict[str, Any] = {
        "model": settings.qwen_model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ],
        "temperature": settings.llm_default_temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {settings.qwen_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                logger.warning("Qwen API HTTP %s: %s", response.status_code, response.text[:500])
                raise QwenServiceError(f"http_{response.status_code}")
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            if not content:
                raise QwenServiceError("empty_response")
            return str(content).strip()
    except QwenServiceError:
        raise
    except Exception as exc:
        logger.warning("Qwen API failed: %s", exc)
        raise QwenServiceError(str(exc)) from exc


async def generate_json(prompt: str) -> dict[str, Any]:
    text = await generate_text(prompt, json_mode=True)
    parsed = _extract_json(text)
    if not parsed:
        raise QwenServiceError("invalid_json")
    return parsed
