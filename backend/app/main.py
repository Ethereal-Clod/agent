"""FastAPI 入口文件。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import appliances as appliances_router
from app.api.endpoints import auth as auth_router
from app.api.endpoints import dashboard as dashboard_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.project_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_router.router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
app.include_router(
    appliances_router.router, prefix=f"{settings.api_prefix}/appliances", tags=["Appliances"]
)
app.include_router(
    dashboard_router.router, prefix=f"{settings.api_prefix}/data", tags=["Dashboard"]
)


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """健康检查：用于部署或监控探针。"""

    return {"status": "ok"}

