import logging
from typing import Any

import httpx

from app.config import Settings, get_settings


logger = logging.getLogger(__name__)


class OllamaService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.ollama_base_url.rstrip("/")
        self._generate_unavailable = False
        self._embed_unavailable = False

    async def health(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                models = [model.get("name", "") for model in data.get("models", [])]
                return {"status": "ok", "models": models}
        except Exception as exc:
            logger.warning("Ollama health check failed: %s", exc)
            return {"status": "unavailable", "models": [], "error": str(exc)}

    async def generate(self, prompt: str, model: str | None = None, temperature: float = 0.2) -> str | None:
        if self._generate_unavailable:
            return None
        payload = {
            "model": model or self.settings.ollama_main_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds * 3) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                return response.json().get("response", "").strip()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                self._generate_unavailable = True
            logger.warning("Ollama generation failed: %s", exc)
            return None
        except Exception as exc:
            logger.warning("Ollama generation failed: %s", exc)
            return None

    async def embed(self, text: str, model: str | None = None) -> list[float] | None:
        if self._embed_unavailable:
            return None
        model_name = model or self.settings.ollama_embed_model
        payload = {"model": model_name, "input": text}
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds * 2) as client:
                response = await client.post(f"{self.base_url}/api/embed", json=payload)
                response.raise_for_status()
                data = response.json()
                embeddings = data.get("embeddings")
                embedding = embeddings[0] if isinstance(embeddings, list) and embeddings else data.get("embedding")
                if isinstance(embedding, list):
                    return [float(value) for value in embedding]
        except httpx.HTTPStatusError as exc:
            logger.warning("Ollama /api/embed failed: %s", exc)
        except Exception as exc:
            logger.warning("Ollama /api/embed failed: %s", exc)

        legacy_payload = {"model": model_name, "prompt": text}
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds * 2) as client:
                response = await client.post(f"{self.base_url}/api/embeddings", json=legacy_payload)
                response.raise_for_status()
                embedding = response.json().get("embedding")
                if isinstance(embedding, list):
                    return [float(value) for value in embedding]
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                self._embed_unavailable = True
            logger.warning("Ollama legacy /api/embeddings failed: %s", exc)
        except Exception as exc:
            logger.warning("Ollama legacy /api/embeddings failed: %s", exc)
        return None
