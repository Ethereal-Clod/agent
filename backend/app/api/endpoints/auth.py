"""身份认证相关接口。"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import (
    MAX_PASSWORD_LENGTH,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, Token, UserCreate, UserRead
from app.models.electricity_account import ElectricityAccount

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """创建新用户账户。"""

    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    try:
        hashed_password = get_password_hash(user_in.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    new_user = User(username=user_in.username, address=user_in.address, password=hashed_password)
    db.add(new_user)
    db.flush()  # 立即获取 user.id，但不提交事务

    # 2. 自动创建用电账户
    account_number = f"A{new_user.id:06d}"  # 生成账号如 ACC000001
    electricity_account = ElectricityAccount(
        user_id=new_user.id,
        account_number=account_number,
        peak_rate=0.8,    # 默认峰值电价
        valley_rate=0.3   # 默认谷值电价
    )
    db.add(electricity_account)
    
    # 3. 提交事务
    db.commit()
    db.refresh(new_user)  # 刷新用户数据（包含关系）
    return new_user


@router.post("/token", response_model=Token)
def login(login_req: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """验证用户凭证并返回访问令牌。"""

    if len(login_req.password) > MAX_PASSWORD_LENGTH:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码长度不能超过 30 个字符")

    user = db.query(User).filter(User.username == login_req.username).first()
    if user is None or not verify_password(login_req.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(subject=user.username, expires_delta=expires)
    return Token(access_token=token, expires_in=int(expires.total_seconds()))


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    """获取当前登录用户信息。"""

    return current_user


@router.post("/logout")
def logout() -> dict[str, str]:
    """简单返回前端可用的提示信息。"""

    return {"message": "已退出登录（前端请删除 Token）"}

