"""仪表盘数据相关接口。"""

import math
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from decimal import Decimal

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.appliance import Appliance
from app.models.consumption_data import ConsumptionData
from app.models.user import User
from app.schemas.dashboard import (
    ChartDataPoint,
    ConsumptionFactors,
    ConsumptionFactor,
    ConsumptionTrend,
    DashboardSummary,
    Weather,
    ElectricityRate,
)

router = APIRouter()


def _calculate_current_power(appliances: List[Appliance]) -> float:
    """计算当前总功率（基于开启的电器）。"""
    return sum(
        float(appliance.power_rating_kw) for appliance in appliances if appliance.is_on
    )


def _estimate_daily_cost(
    appliances: List[Appliance], peak_rate: Decimal, valley_rate: Decimal
) -> float:
    """估算今日电费（基于当前开启的电器和平均使用时长）。"""
    # 简单估算：假设开启的电器平均每天使用8小时，使用平均电价
    avg_rate = (float(peak_rate) + float(valley_rate)) / 2
    total_power = _calculate_current_power(appliances)
    # 假设当前开启的电器会持续使用，按8小时估算
    estimated_hours = 8.0
    return total_power * estimated_hours * avg_rate


def _get_month_usage(db: Session, account_id: int) -> float:
    """获取本月累计用电量（kWh）。"""
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    
    result = (
        db.query(func.sum(ConsumptionData.total_kwh))
        .filter(
            and_(
                ConsumptionData.account_id == account_id,
                ConsumptionData.timestamp >= month_start,
            )
        )
        .scalar()
    )
    return float(result) if result else 0.0


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardSummary:
    """获取今日概览（KPI Cards）。"""
    if not current_user.electricity_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户还没有用电账户",
        )

    account = current_user.electricity_account
    appliances = (
        db.query(Appliance)
        .filter(Appliance.account_id == account.id)
        .all()
    )

    # 计算当前总功率
    total_power_now = _calculate_current_power(appliances)

    # 估算今日电费
    daily_cost_estimate = _estimate_daily_cost(
        appliances, account.peak_rate, account.valley_rate
    )

    # 获取本月累计用电
    month_usage_kwh = _get_month_usage(db, account.id)

    # 统计开启的电器数量
    active_appliances_count = sum(1 for app in appliances if app.is_on)

    return DashboardSummary(
        total_power_now=round(total_power_now, 2),
        daily_cost_estimate=round(daily_cost_estimate, 2),
        month_usage_kwh=round(month_usage_kwh, 2),
        active_appliances_count=active_appliances_count,
    )


def _generate_mock_trend_data(
    range_type: str, account_id: int, db: Session, appliances: List[Appliance]
) -> List[ChartDataPoint]:
    """生成模拟趋势数据（当数据库中没有真实数据时）。返回格式匹配前端期望。"""
    now = datetime.now()
    data = []

    # 计算基础用电量（基于开启的电器）
    base_power_w = sum(
        float(app.power_rating_kw) * 1000  # 转换为瓦特
        for app in appliances
        if app.is_on
    )

    if range_type == "24h":
        # 生成过去24小时的数据，每30分钟一个点（48个点）
        for i in range(48, 0, -1):
            timestamp = now - timedelta(minutes=30 * i)
            time_str = timestamp.strftime("%H:%M")
            
            # 模拟数据：白天高，夜间低，加上基础用电
            hour = timestamp.hour
            if hour >= 7 and hour <= 9:
                # 早晨高峰
                usage = base_power_w + 150 + (i % 5) * 50
            elif hour >= 18 and hour <= 22:
                # 晚上高峰
                usage = base_power_w + 300 + (i % 5) * 100
            elif hour >= 12 and hour <= 14:
                # 中午
                usage = base_power_w + 100 + (i % 3) * 30
            else:
                # 其他时间（基础待机）
                usage = base_power_w + 50 + (i % 3) * 20
            
            data.append(ChartDataPoint(
                time=time_str,
                usage=round(max(100, usage), 0)  # 最小100W，单位：瓦特
            ))
    elif range_type == "week":
        # 生成过去7天的数据，每天一个点
        for i in range(7, 0, -1):
            date = now.date() - timedelta(days=i)
            time_str = date.strftime("%m/%d")
            # 模拟数据：工作日稍高
            weekday_factor = 1.2 if date.weekday() < 5 else 1.0
            usage = (base_power_w * 24 * weekday_factor) + (i % 3) * 2000  # 每天的总用电量（W）
            data.append(ChartDataPoint(
                time=time_str,
                usage=round(usage, 0)
            ))
    else:  # month
        # 生成过去30天的数据，每3天一个点
        for i in range(30, 0, -3):
            date = now.date() - timedelta(days=i)
            time_str = date.strftime("%m/%d")
            usage = (base_power_w * 24 * 3) + (i % 10) * 3000  # 每3天的总用电量（W）
            data.append(ChartDataPoint(
                time=time_str,
                usage=round(usage, 0)
            ))

    return data


@router.get("/consumption/trend", response_model=ConsumptionTrend)
def get_consumption_trend(
    range: str = Query("24h", description="时间范围: 24h, week, month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConsumptionTrend:
    """获取用电趋势（折线图数据），返回格式匹配前端期望。"""
    if not current_user.electricity_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户还没有用电账户",
        )

    if range not in ["24h", "week", "month"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="range 参数必须是 24h, week 或 month",
        )

    account = current_user.electricity_account
    appliances = (
        db.query(Appliance)
        .filter(Appliance.account_id == account.id)
        .all()
    )
    
    now = datetime.now()

    # 根据时间范围确定查询的起始时间
    if range == "24h":
        start_time = now - timedelta(hours=24)
        time_format = "%H:%M"
    elif range == "week":
        start_time = now - timedelta(days=7)
        time_format = "%m/%d"
    else:  # month
        start_time = now - timedelta(days=30)
        time_format = "%m/%d"

    # 查询数据库中的真实数据
    records = (
        db.query(ConsumptionData)
        .filter(
            and_(
                ConsumptionData.account_id == account.id,
                ConsumptionData.timestamp >= start_time,
            )
        )
        .order_by(ConsumptionData.timestamp)
        .all()
    )

    if records:
        # 有真实数据，转换为前端期望的格式（kWh -> W）
        data = []
        for record in records:
            # 将 kWh 转换为 W（假设是30分钟内的用电量）
            usage_w = float(record.total_kwh) * 1000 * 2  # 转换为瓦特，并假设是30分钟内的功率
            data.append(ChartDataPoint(
                time=record.timestamp.strftime(time_format),
                usage=round(usage_w, 0)
            ))
    else:
        # 没有真实数据，生成模拟数据
        data = _generate_mock_trend_data(range, account.id, db, appliances)

    return ConsumptionTrend(data=data)


@router.get("/consumption/factors", response_model=ConsumptionFactors)
def get_consumption_factors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConsumptionFactors:
    """获取用电影响因素（AI 分析数据）。"""
    if not current_user.electricity_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户还没有用电账户",
        )

    account = current_user.electricity_account
    appliances = (
        db.query(Appliance)
        .filter(Appliance.account_id == account.id)
        .all()
    )

    # 分析当前电器状态，生成影响因素
    total_power = sum(float(app.power_rating_kw) for app in appliances)
    active_power = sum(
        float(app.power_rating_kw) for app in appliances if app.is_on
    )

    # 计算各因素权重（模拟AI分析）
    factors = []

    # 天气因素（如果有空调或暖气开启）
    ac_heater_on = any(
        app.is_on and app.type in ["ac", "heater"] for app in appliances
    )
    weather_factor = 40.0 if ac_heater_on else 10.0
    factors.append(
        ConsumptionFactor(name="天气因素 (制冷/制热)", value=weather_factor)
    )

    # 大功率电器使用
    large_appliances_power = sum(
        float(app.power_rating_kw)
        for app in appliances
        if app.is_on and float(app.power_rating_kw) > 1.0
    )
    large_app_factor = min(50.0, (large_appliances_power / total_power * 100) if total_power > 0 else 0)
    factors.append(
        ConsumptionFactor(name="大功率电器使用", value=round(large_app_factor, 1))
    )

    # 基础待机
    standby_factor = 15.0
    factors.append(ConsumptionFactor(name="基础待机", value=standby_factor))

    # 峰时用电（根据当前时间判断）
    current_hour = datetime.now().hour
    is_peak_time = 8 <= current_hour <= 22
    peak_factor = 20.0 if is_peak_time else 5.0
    factors.append(ConsumptionFactor(name="峰时用电", value=peak_factor))

    # 归一化因子值，使总和为100
    total_value = sum(f.value for f in factors)
    if total_value > 0:
        normalized_factors = []
        for factor in factors:
            normalized_value = round(factor.value / total_value * 100, 1)
            normalized_factors.append(
                ConsumptionFactor(name=factor.name, value=normalized_value)
            )
        factors = normalized_factors

    # 生成AI建议
    if ac_heater_on:
        suggestion = "检测到空调/暖气正在运行，建议适当调整温度设置以平衡舒适度和节能。"
    elif large_app_factor > 30:
        suggestion = "当前大功率电器使用较多，建议错峰使用以降低电费成本。"
    else:
        suggestion = "当前用电情况良好，继续保持节能习惯！"

    return ConsumptionFactors(
        updated_at=datetime.now(),
        factors=factors,
        suggestion=suggestion,
    )


@router.get("/weather", response_model=Weather)
def get_weather(
    current_user: User = Depends(get_current_user),
) -> Weather:
    """获取天气数据（模拟数据，后续可接入真实天气API）。"""
    now = datetime.now()
    hour = now.hour

    # 模拟天气数据（类似前端demo的逻辑）
    def get_condition(h: int) -> str:
        if h > 18 or h < 6:
            return "晴朗"
        if h > 10 and h < 16:
            return "炎热"
        return "多云"

    # 模拟温度变化（类似前端demo）
    temperature_c = 22 + math.sin(hour / 12 * math.pi) * 8
    
    condition = get_condition(hour)
    humidity = 60 + math.cos(hour / 12 * math.pi) * 15

    return Weather(
        temperatureC=round(temperature_c, 1),
        condition=condition,
        humidity=round(humidity, 0),
    )


@router.get("/electricity-rate", response_model=ElectricityRate)
def get_electricity_rate(
    current_user: User = Depends(get_current_user),
) -> ElectricityRate:
    """获取当前电价状态（根据时间判断）。"""
    now = datetime.now()
    hour = now.hour

    # 根据时间判断电价（匹配前端demo的逻辑）
    if hour >= 18 and hour < 22:
        rate = "peak"
        rate_text = "峰值电价"
    elif hour >= 0 and hour < 7:
        rate = "valley"
        rate_text = "谷值电价"
    else:
        rate = "normal"
        rate_text = "平值电价"

    return ElectricityRate(rate=rate, rateText=rate_text)

