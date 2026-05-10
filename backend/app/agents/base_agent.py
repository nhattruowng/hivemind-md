import logging
from abc import ABC, abstractmethod
from typing import Any


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    name: str = "BaseAgent"
    description: str = "Base agent"

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        logger.info("%s started", self.name)
        try:
            result = await self.run(**kwargs)
            logger.info("%s finished: %s", self.name, result.get("message", "done"))
            return result
        except Exception as exc:
            logger.exception("%s failed", self.name)
            return self.failed(str(exc))

    @abstractmethod
    async def run(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def success(self, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "success",
            "message": message,
            "data": data or {},
        }

    def failed(self, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "failed",
            "message": message,
            "data": data or {},
        }

