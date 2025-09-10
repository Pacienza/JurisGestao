from __future__ import annotations
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Caminho absoluto para o banco SQLite persistente
DB_PATH = Path("juris.db").resolve()

# Criação do engine com echo desabilitado
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)

# Sessão de banco de dados
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Ativa foreign_keys e modo WAL no SQLite (melhora integridade e performance)
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.close()

# Base para todos os modelos ORM
class Base(DeclarativeBase):
    pass
