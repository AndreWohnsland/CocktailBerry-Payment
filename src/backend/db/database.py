import asyncio
import logging
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from shutil import copy2

from sqlmodel import Session, SQLModel, create_engine

from src.backend.core.config import config as cfg

_logger = logging.getLogger(__name__)

DATABASE_PATH = Path(cfg.database_path)
BACKUP_DIR = DATABASE_PATH.parent / "backups"
BACKUP_DIR.mkdir(exist_ok=True, parents=True)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


async def backup_db_periodically() -> None:
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"payment_{timestamp}.sqlite"
        copy2(DATABASE_PATH, backup_file)
        _logger.info(f"Backup created: {backup_file}")
        await asyncio.sleep(12 * 60 * 60)  # every 12 hours


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
