from fastapi import APIRouter

from app.services.ollama_service import OllamaService


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "HiveMind MD Backend"}


@router.get("/health/ollama")
async def ollama_health() -> dict[str, object]:
    return await OllamaService().health()

