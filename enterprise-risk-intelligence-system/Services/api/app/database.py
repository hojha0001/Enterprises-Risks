# Services/api/app/db.py
from pathlib import Path
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session

DB_PATH = Path(__file__).resolve().parent / "risk.db"   # CWD issues solved
sqlite_url = f"sqlite:///{DB_PATH}"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})

def init_db() -> None:
    # IMPORTANT: import models before create_all so tables register
    from . import models  # noqa: F401
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
