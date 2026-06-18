"""Alembic environment for the CocktailBerry Payment backend.

Migrations target ``SQLModel.metadata``; the model modules are imported below so
their tables register on it. ``render_as_batch=True`` is required for SQLite,
which cannot ``ALTER`` columns in place — batch mode recreates the table instead.
"""

from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context
from src.backend.core.config import config as app_config
from src.backend.models import user  # noqa: F401  (import registers tables on SQLModel.metadata)

config = context.config

if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def get_database_url() -> str:
    """Resolve the database URL.

    Prefer an explicit URL set on the Alembic config (the runtime helper
    ``run_db_migrations`` sets it), so the caller stays authoritative. Fall back
    to the application config for the bare CLI, where ``alembic.ini`` only holds
    the ``sqlite:///`` placeholder.
    """
    configured = config.get_main_option("sqlalchemy.url")
    if configured and configured != "sqlite:///":
        return configured
    return f"sqlite:///{app_config.database_path}"


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (emits SQL)."""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live DB connection."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
