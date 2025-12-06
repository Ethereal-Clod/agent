"""仪表盘相关的 Pydantic 模型。"""

from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    """今日概览（KPI Cards）响应模型。"""

    total_power_now: float = Field(..., description="当前总功率 (kW)")
    daily_cost_estimate: float = Field(..., description="今日预计电费 (元)")
    month_usage_kwh: float = Field(..., description="本月累计用电 (kWh)")
    active_appliances_count: int = Field(..., description="开启的电器数量")


class ChartDataPoint(BaseModel):
    """图表数据点。"""

    time: str = Field(..., description="时间点，格式 HH:MM 或 MM/DD")
    usage: float = Field(..., description="用电量 (W，瓦特)")


class ConsumptionTrend(BaseModel):
    """用电趋势响应模型（匹配前端格式）。"""

    data: List[ChartDataPoint] = Field(..., description="用电趋势数据点列表")


class ConsumptionFactor(BaseModel):
    """用电影响因素项。"""

    name: str = Field(..., description="因素名称")
    value: float = Field(..., ge=0, le=100, description="影响权重 (0-100)")


class ConsumptionFactors(BaseModel):
    """用电影响因素响应模型。"""

    updated_at: datetime = Field(..., description="数据更新时间")
    factors: List[ConsumptionFactor] = Field(..., description="影响因素列表")
    suggestion: str = Field(..., description="AI 节能建议")


class Weather(BaseModel):
    """天气数据响应模型。"""

    temperatureC: float = Field(..., description="温度 (°C)")
    condition: str = Field(..., description="天气状况")
    humidity: float = Field(..., description="湿度 (%)")


class ElectricityRate(BaseModel):
    """电价状态响应模型。"""

    rate: Literal["peak", "normal", "valley"] = Field(..., description="电价类型")
    rateText: str = Field(..., description="电价文本描述")

