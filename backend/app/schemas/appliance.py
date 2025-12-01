"""电器相关的 Pydantic 模型。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApplianceCreate(BaseModel):
    """创建电器时需要的参数。"""

    name: str = Field(..., min_length=1, max_length=100, description="电器名称")
    type: str = Field(..., description="电器类型: ac, fridge, light, tv, heater, other")
    power_rating: float = Field(..., ge=0, description="额定功率(kW)")
    location: str = Field(default="Living Room", max_length=50, description="位置")


class ApplianceOut(BaseModel):
    """返回给前端的电器信息。"""

    id: int
    name: str
    type: str
    is_on: bool
    power_rating_kw: float
    created_at: datetime

    class Config:
        from_attributes = True


class ApplianceControl(BaseModel):
    """控制电器开关时的参数。"""

    action: str = Field(..., description="操作: ON 或 OFF")


class ControlResponse(BaseModel):
    """AI 控制响应。"""

    success: bool
    appliance_id: int
    new_status: bool
    ai_message: str  # AI 的建议

