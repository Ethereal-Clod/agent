"""FastAPI 依赖项集合。"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from typing import Generator


# 定义安全模式为 HTTP Bearer
reusable_oauth2 = HTTPBearer(
    scheme_name="Authorization", 
    description="请输入 Token (格式: Bearer <token>)"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_current_user(
    token_auth: HTTPAuthorizationCredentials = Depends(reusable_oauth2), 
    db: Session = Depends(get_db),
) -> User:
    """解析 JWT 并获取对应用户。"""
    
    # 手动提取 token 字符串
    token = token_auth.credentials
    
    try:
        # 修复：使用正确的配置属性
        payload = jwt.decode(
            token, 
            settings.secret_key,  # ✅ 修复：使用小写的 secret_key
            algorithms=[settings.jwt_algorithm]  # ✅ 修复：使用正确的算法
        )
        token_data = payload
    except (JWTError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="凭证无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 确保这里用的 key 和生成 token 时的一样，通常是 "sub"
    username = token_data.get("sub") 
    
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token 缺少用户信息"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="用户不存在"
        )
    
    return user


