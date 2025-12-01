"""电器 ORM 模型。"""

import enum
from datetime import datetime

from sqlalchemy import BIGINT,Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class ApplianceType(str, enum.Enum):
    """电器类型枚举。"""

    ac = "ac"  # 空调
    fridge = "fridge"  # 冰箱
    light = "light"  # 照明
    tv = "tv"  # 电视
    heater = "heater"  # 热水器/暖气
    other = "other"  # 其他


class Appliance(Base):
    """对应 `appliances` 表的实体。"""

    __tablename__ = "appliances"

    id = Column(BIGINT, primary_key=True, index=True)
    account_id = Column(BIGINT, ForeignKey("electricity_accounts.id"), nullable=False, comment="所属用电账户ID")
    name = Column(String(100), nullable=False, comment="电器名称")
    type = Column(Enum(ApplianceType), nullable=False, comment="电器类型")
    is_on = Column(Boolean, default=False, comment="当前开关状态")
    power_rating_kw = Column(Float, default=0.0, comment="额定功率(kW)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

   # 注意：appliances 表通过 electricity_accounts 中间表关联到用户
   # 这种设计支持峰谷电价等复杂计费策略

    account = relationship("ElectricityAccount", back_populates="appliances")


    def __repr__(self) -> str:
        return f"<Appliance name={self.name} type={self.type} is_on={self.is_on}>"

