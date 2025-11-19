from fastapi import FastAPI

app = FastAPI(
    title="🏡 AI 用电助手 (家庭版) API",
    description="为 AI 用电助手前端提供后端服务的 API。",
    version="1.0.0",
)

@app.get("/")
def a_read_root():
    """
    健康检查接口，确认服务是否成功启动。
    """
    return {"status": "ok", "message": "欢迎来到 AI 用电助手 API！"}