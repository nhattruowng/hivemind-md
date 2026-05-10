import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent_framework_routes import router as agent_framework_router
from app.api.agent_routes import router as agent_router
from app.api.chat_routes import router as chat_router
from app.api.health_routes import router as health_router
from app.api.knowledge_routes import router as knowledge_router
from app.api.self_improvement_routes import router as self_improvement_router
from app.config import get_settings
from app.database import init_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(health_router)
app.include_router(agent_framework_router)
app.include_router(agent_router)
app.include_router(knowledge_router)
app.include_router(chat_router)
app.include_router(self_improvement_router)
