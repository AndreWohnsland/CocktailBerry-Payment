from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.api.routes import api_router
from src.backend.core.config import config as cfg
from src.backend.core.log_config import log_config
from src.backend.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    init_db()
    yield
    # Shutdown


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
    uvicorn.run(app, host="0.0.0.0", port=cfg.api_port, log_config=log_config)
