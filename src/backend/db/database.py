import asyncio
import logging
import sqlite3
from collections.abc import Generator
from contextlib import closing
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from src.backend.core.config import config as cfg

_logger = logging.getLogger(__name__)

DATABASE_PATH = Path(cfg.database_path)
BACKUP_DIR = DATABASE_PATH.parent / "backups"
BACKUP_DIR.mkdir(exist_ok=True, parents=True)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

BACKUP_INTERVAL_SECONDS = 12 * 60 * 60  # every 12 hours
BACKUP_RETENTION = 14  # keep the 14 newest backups (~7 days at a 12h interval)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def _create_backup() -> None:
    """Write a transactionally-consistent snapshot via SQLite's online backup API."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"payment_{timestamp}.sqlite"
    # Unlike a raw file copy, .backup() snapshots a consistent state even while
    # the DB is being written to, and produces a single file with no WAL sidecar.
    with closing(sqlite3.connect(DATABASE_PATH)) as source, closing(sqlite3.connect(backup_file)) as target:
        source.backup(target)
    _logger.info(f"Backup created: {backup_file}")
    _prune_backups()


def _prune_backups() -> None:
    """Delete all but the most recent BACKUP_RETENTION backups."""
    # The zero-padded timestamp in the name makes lexical sort == chronological.
    backups = sorted(BACKUP_DIR.glob("payment_*.sqlite"))
    for old in backups[:-BACKUP_RETENTION]:
        old.unlink(missing_ok=True)
        _logger.info(f"Removed old backup: {old}")


async def backup_db_periodically() -> None:
    while True:
        try:
            await asyncio.to_thread(_create_backup)
        except Exception:
            _logger.exception("Database backup failed")
        await asyncio.sleep(BACKUP_INTERVAL_SECONDS)


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def run_db_migrations() -> None:
    """Bring the database schema up to the latest Alembic revision.

    Configures Alembic programmatically so it works identically from a source
    checkout, via ``uv run``, or inside the Docker image (which only copies
    ``src/`` and so does not include the root ``alembic.ini``). The script
    location is resolved relative to this package rather than the cwd.

    Handles three cases:

    * **Fresh database** — ``upgrade`` runs every migration from the baseline,
      creating all tables.
    * **Pre-Alembic database** (schema built by the old ``create_all`` path, so
      it has the tables but no ``alembic_version``) — adopt it at the baseline
      revision via ``stamp`` so the baseline migration is not re-run against
      existing tables, then ``upgrade`` applies anything newer.
    * **Already managed database** — ``upgrade`` applies pending migrations.
    """
    from alembic import command
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    from sqlalchemy import inspect

    migrations_dir = Path(__file__).resolve().parent / "migrations"
    alembic_cfg = Config()
    alembic_cfg.attributes["configure_logger"] = False
    alembic_cfg.set_main_option("script_location", str(migrations_dir))
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

    inspector = inspect(engine)
    pre_alembic = inspector.has_table("users") and not inspector.has_table("alembic_version")
    if pre_alembic:
        bases = ScriptDirectory.from_config(alembic_cfg).get_bases()
        if bases:
            command.stamp(alembic_cfg, bases[0])
    command.upgrade(alembic_cfg, "head")
