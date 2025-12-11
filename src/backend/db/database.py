from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

DATABASE_PATH = Path.home() / ".cocktailberry" / "payment.db"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
