from __future__ import annotations
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

APP_DIR = Path.home() / ".jurisgestao"
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "jurisgestao.sqlite3"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},  # SQLite + UI thread
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass
