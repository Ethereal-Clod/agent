"""用电数据 ORM 模型。"""

from datetime import datetime

from sqlalchemy import BIGINT, Column, DateTime, DECIMAL, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class ConsumptionData(Base):
    """对应 `consumption_data` 表的实体。"""

    __tablename__ = "consumption_data"

    id = Column(BIGINT, primary_key=True, index=True)
    account_id = Column(BIGINT, ForeignKey("electricity_accounts.id"), nullable=False, comment="关联的用电账户ID")
    timestamp = Column(DateTime(timezone=True), nullable=False, comment="数据记录时间点")
    total_kwh = Column(DECIMAL(10, 3), nullable=False, comment="该时间片内的总耗电量 (kWh)")

    # 关系定义
    account = relationship("ElectricityAccount", back_populates="consumption_records")

    def __repr__(self) -> str:
        return f"<ConsumptionData account_id={self.account_id} timestamp={self.timestamp} total_kwh={self.total_kwh}>"

