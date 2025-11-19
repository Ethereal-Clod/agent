"""数据库会话与引擎管理。"""

from pathlib import Path
from typing import Generator, Optional, Dict, Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


def _build_connect_args(database_url: str) -> Optional[Dict[str, Any]]:
    """针对 SQLite 提供额外连接参数，其它数据库返回 None。"""

    if database_url.startswith("sqlite"):
        Path("data").mkdir(parents=True, exist_ok=True)
        return {"check_same_thread": False}
    return None


engine: Engine = create_engine(
    settings.database_url,
    echo=False,
    future=True,
    connect_args=_build_connect_args(settings.database_url) or {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖项：提供一个数据库会话，并在请求结束时自动关闭。"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


