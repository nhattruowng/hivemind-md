import logging
from abc import ABC, abstractmethod
from time import perf_counter
from typing import Any


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    name: str = "BaseAgent"
    description: str = "Base agent"

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        logger.info("%s started", self.name)
        started = perf_counter()
        try:
            result = await self.run(**kwargs)
            result.setdefault("runtime_ms", int((perf_counter() - started) * 1000))
            result.setdefault("confidence", None)
            result.setdefault("sources", [])
            result.setdefault("tool_calls", [])
            result.setdefault("risk_level", "low")
            logger.info("%s finished: %s", self.name, result.get("message", "done"))
            return result
        except Exception as exc:
            logger.exception("%s failed", self.name)
            return self.failed(str(exc), runtime_ms=int((perf_counter() - started) * 1000))

    @abstractmethod
    async def run(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def success(
        self,
        message: str,
        data: dict[str, Any] | None = None,
        *,
        confidence: float | None = None,
        sources: list[Any] | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
        risk_level: str = "low",
        runtime_ms: int = 0,
    ) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "success",
            "message": message,
            "data": data or {},
            "confidence": confidence,
            "sources": sources or [],
            "tool_calls": tool_calls or [],
            "risk_level": risk_level,
            "runtime_ms": runtime_ms,
        }

    def failed(
        self,
        message: str,
        data: dict[str, Any] | None = None,
        *,
        confidence: float | None = 0.0,
        sources: list[Any] | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
        risk_level: str = "low",
        runtime_ms: int = 0,
    ) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "failed",
            "message": message,
            "data": data or {},
            "confidence": confidence,
            "sources": sources or [],
            "tool_calls": tool_calls or [],
            "risk_level": risk_level,
            "runtime_ms": runtime_ms,
        }
