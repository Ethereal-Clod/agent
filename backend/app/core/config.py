"""应用配置模块。

该文件集中管理所有与环境相关的配置项，便于在开发、测试、
生产之间切换。默认提供一个可快速启动的 SQLite 数据库连接，
如果需要连接 MySQL，只需在 `.env` 中覆盖 `DATABASE_URL`。
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置对象，所有子模块通过依赖注入访问。"""

    project_name: str = "AI 用电助手 · 后端"
    api_prefix: str = "/api"

    # 数据库配置：默认连接本地 MySQL，可通过 .env 覆盖
    database_url: str = "mysql+pymysql://group-user:123456@localhost:3306/ai_power_db"

    # JWT 安全配置
    secret_key: str = "a_very_secret_key_that_should_be_in_env_file"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """启用 LRU 缓存，避免频繁重新读取环境变量。"""

    return Settings()


settings = get_settings()

