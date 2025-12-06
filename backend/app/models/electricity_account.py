from sqlalchemy import BIGINT, Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class ElectricityAccount(Base):
    __tablename__ = "electricity_accounts"

    id = Column(BIGINT, primary_key=True, index=True)
    # 这里 user_id 必须唯一，对应 SQL 中的 UNIQUE
    user_id = Column(BIGINT, ForeignKey("users.id"), unique=True, nullable=False)
    account_number = Column(String(50), unique=True, comment="账户编号")
    peak_rate = Column(DECIMAL(10, 4), default=0.8, comment="峰值电价")
    valley_rate = Column(DECIMAL(10, 4), default=0.3, comment="谷值电价")

    # 关系定义
    user = relationship("User", back_populates="electricity_account")
    appliances = relationship("Appliance", back_populates="account")
    consumption_records = relationship("ConsumptionData", back_populates="account")