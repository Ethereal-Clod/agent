"""用户 ORM 模型。"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, func

from app.db.base import Base


class User(Base):
    """对应 `users` 表的实体。"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(30), nullable=False)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<User username={self.username}>"


