import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.api.routes import api_router
from src.backend.core.config import config as cfg
from src.backend.db.database import backup_db_periodically, get_db, init_db
from src.backend.models.user import UserCreate
from src.backend.service.user_service import get_user_service
from src.shared import LOG_CONFIG_PATH


def initialize_master_key_users() -> None:
    """Create users for master keys if they don't exist."""
    user_service = get_user_service(next(get_db()))

    for master_key in cfg.master_keys:
        existing_user = user_service.get_user_by_nfc(master_key)
        if not existing_user:
            user_service.create_user(UserCreate(nfc_id=master_key, is_adult=True, balance=100.0))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # Startup
    init_db()
    initialize_master_key_users()
    backups = asyncio.create_task(backup_db_periodically())
    yield
    # Shutdown
    backups.cancel()


app = FastAPI(
    title="CocktailBerry Payment API",
    description="Payment and balance management service for CocktailBerry",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "CocktailBerry Payment API"}


def run_with_uvicorn() -> None:
    uvicorn.run(app, host="0.0.0.0", port=cfg.api_port, log_config=str(LOG_CONFIG_PATH))
