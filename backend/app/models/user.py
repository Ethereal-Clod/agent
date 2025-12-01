"""用户 ORM 模型。"""

from datetime import datetime

from sqlalchemy import BIGINT,Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """对应 `users` 表的实体。"""

    __tablename__ = "users"

    id = Column(BIGINT, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(30), nullable=False)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # 建立反向关系，方便通过 user.account查到所有电器
    electricity_account = relationship("ElectricityAccount", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User username={self.username}>"


