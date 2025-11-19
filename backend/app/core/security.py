"""安全相关工具函数：密码哈希与 JWT。"""

from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any, Dict

from jose import JWTError, jwt

from app.core.config import settings

MAX_PASSWORD_LENGTH = 30


def _ensure_length(password: str) -> str:
    """确认密码不超过 30 个字符。"""

    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError("密码长度不能超过 30 个字符")
    return password


def _digest(password: str) -> str:
    """对密码进行 SHA-256 哈希，并截取前 30 个字符用于存储。"""

    sha_hex = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return sha_hex[:MAX_PASSWORD_LENGTH]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与哈希值是否匹配。"""

    try:
        expected = get_password_hash(plain_password)
    except ValueError:
        return False
    return expected == hashed_password


def get_password_hash(password: str) -> str:
    """生成密码哈希（最终长度不超过 30 个字符）。"""

    normalized = _ensure_length(password)
    return _digest(normalized)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """创建 JWT 访问令牌。"""

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode: Dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


class TokenDecodeError(Exception):
    """包装 JWT 解码异常，方便统一处理。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def decode_access_token(token: str) -> Dict[str, Any]:
    """解码 JWT，失败时抛出自定义异常。"""

    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:  # pragma: no cover - 只在异常路径执行
        raise TokenDecodeError("Token 无效或已过期") from exc

