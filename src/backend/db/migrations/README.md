# Database migrations (Alembic)

This directory holds the Alembic setup for the payment backend. It is **live**:
on startup the app calls `run_db_migrations()` (`../database.py`), which runs
`alembic upgrade head`. The schema is owned by the migrations in `versions/`,
starting from the baseline revision.

## How it's set up (and why)

- **`../../../../alembic.ini`** (repo root) — for the dev CLI only.
- **`env.py`** — targets `SQLModel.metadata` (the model modules are imported so
  their tables register) and resolves the DB URL from the Alembic config when
  set (the runtime helper sets it), otherwise from the app config
  (`src.backend.core.config`). CLI and app therefore always touch the same DB.
- **`render_as_batch=True`** — required for SQLite: it cannot `ALTER` a column in
  place, so Alembic recreates the table inside a batch operation. Without this,
  column type/constraint changes fail on SQLite.
- **`compare_type=True`** — so autogenerate notices column *type* changes.
- The migration scripts live under `src/` on purpose: the Docker image only does
  `COPY src ./src`, so anything outside `src/` (including `alembic.ini`) is absent
  at runtime. The runtime helper therefore configures Alembic programmatically.

## Startup behaviour (`run_db_migrations`)

Handles all three database states automatically — no manual step on deploy:

- **Fresh database** → `upgrade` runs from the baseline and creates every table.
- **Pre-Alembic database** (built by the old `create_all` path: tables exist, no
  `alembic_version`) → it is `stamp`ed at the baseline revision (adopted without
  re-running `CREATE TABLE`), then `upgrade` applies anything newer.
- **Already-managed database** → `upgrade` applies pending migrations.

This was verified against fresh DBs, a populated pre-Alembic DB, and the real
`data/payment.db` (data preserved, idempotent on repeated runs).

## Creating a migration

1. Change the SQLModel models.
2. Autogenerate (run from the repo root, which has `alembic.ini`):

   ```bash
   uv run --extra api alembic revision --autogenerate -m "describe the change"
   ```

3. **Review the generated file** in `versions/` — autogenerate is a draft, not
   gospel. It does not detect renames or data backfills, and on SQLite column
   changes must go through `op.batch_alter_table(...)` (batch mode is enabled, so
   it usually does this for you — confirm it).
4. Commit the migration file alongside the model change. It is applied
   automatically on the next startup of every install (and via
   `alembic upgrade head` for manual runs).

## Quick reference

```bash
uv run --extra api alembic revision --autogenerate -m "msg"  # create
uv run --extra api alembic upgrade head                      # apply
uv run --extra api alembic downgrade -1                      # roll back one
uv run --extra api alembic history                           # list
uv run --extra api alembic current                           # show DB revision
```
