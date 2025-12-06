"""电器管理相关接口。"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.appliance import Appliance
from app.models.user import User
from app.schemas.appliance import (
    ApplianceControl,
    ApplianceCreate,
    ApplianceOut,
    ControlResponse,
)
from app.services.mock_ai import analyze_appliance_action

router = APIRouter()


@router.post("/", response_model=ApplianceOut, status_code=status.HTTP_201_CREATED)
def create_appliance(
    item: ApplianceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplianceOut:
    """添加新电器（用于初始化数据）。"""
    # 检查用户是否有用电账户
    if not current_user.electricity_account:
        # 如果没有，抛出错误或自动创建（这里选择抛出错误）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户还没有用电账户，请联系管理员"
        )
    
    new_appliance = Appliance(
        name=item.name,
        type=item.type,
        power_rating_kw=item.power_rating,
        account_id=current_user.electricity_account.id,  # ✅ 修改：使用 account_id
    )
    db.add(new_appliance)
    db.commit()
    db.refresh(new_appliance)
    return new_appliance


@router.get("/", response_model=List[ApplianceOut])
def read_appliances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ApplianceOut]:
    """获取当前用户的电器列表。"""
    # 通过 electricity_account 关联查询电器
    if not current_user.electricity_account:
        return []  # 如果没有账户，返回空列表
    
    appliances = db.query(Appliance).filter(
        Appliance.account_id == current_user.electricity_account.id
    ).all()
    return appliances


@router.post("/{appliance_id}/control", response_model=ControlResponse)
def control_appliance(
    appliance_id: int,
    control: ApplianceControl,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ControlResponse:
    """控制电器开关（AI 介入）。"""
    if not current_user.electricity_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户还没有用电账户"
        )
     # 1. 查询电器 - 通过 account_id 关联
    appliance = (
        db.query(Appliance)
        .filter(
            Appliance.id == appliance_id, 
            Appliance.account_id == current_user.electricity_account.id
        )
        .first()
    )

    if not appliance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="电器不存在或不属于你")

    # 2. 更新状态
    action = control.action.upper()  # 转大写 "ON" / "OFF"
    new_is_on = True if action == "ON" else False
    appliance.is_on = new_is_on

    # 3. 调用 AI 分析（模拟）
    ai_message = analyze_appliance_action(appliance.name, action, appliance.power_rating_kw)

    # 4. 保存数据库
    db.commit()

    return ControlResponse(
        success=True,
        appliance_id=appliance.id,
        new_status=new_is_on,
        ai_message=ai_message,
    )

