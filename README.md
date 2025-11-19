# 🏡 AI 用电助手 (家庭版)

一个基于 FastAPI + LangGraph 的家庭用电智能助手后端示例，提供用户认证、数据分析、智能控制与 AI 聊天接口。前端（Vue3）通过 REST API 与该服务交互。

---

## 项目结构

- `backend/app`：FastAPI 源码
  - `core`：配置、加密等通用模块
  - `db`：SQLAlchemy 引擎和 Base
  - `models`：ORM 模型（当前已实现 `User`）
  - `schemas`：Pydantic 数据模型
  - `api/endpoints`：路由定义（首批完成了 Auth）
- `doc/`：系统设计与 API 文档（V2.0）
- `db/schema.sql`：MySQL 数据建表脚本

---

## 快速开始

1. **安装依赖**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/Scripts/activate  # Windows PowerShell
   pip install -r requirements.txt
   ```

2. **配置环境变量（可选）**  
   在 `backend` 目录创建 `.env`：
   ```
   DATABASE_URL=mysql+pymysql://group-user:123456@localhost:3306/ai_power_db
   SECRET_KEY=请替换为随机字符串
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```
   若不配置，将默认连接 `mysql+pymysql://group-user:123456@localhost:3306/ai_power_db`。

3. **初始化数据库**
   - 选择 MySQL：执行 `db/schema.sql`
   - 或 SQLite：首次运行服务会自动建表

4. **启动服务**
   ```bash
   uvicorn app.main:app --reload
   ```
   访问 `http://localhost:8000/docs` 查看自动生成的接口文档。

---

## 认证模块 API

| Method | URL                | 描述           |
|--------|--------------------|----------------|
| POST   | `/api/auth/register` | 注册新用户      |
| POST   | `/api/auth/token`    | 登录并获取 Token |
| GET    | `/api/auth/me`       | 获取当前用户信息 |
| POST   | `/api/auth/logout`   | 退出登录（前端清 Token） |

> 密码规则：长度需在 6~30 个字符之间，系统会在存储前进行截断哈希，最终加密串也不超过 30 个字符。

### 请求示例
```http
POST /api/auth/register
{
  "username": "test001",
  "password": "securePass1",
  "address": "杭州市西湖区"
}
```

```http
POST /api/auth/token
{
  "username": "test001",
  "password": "securePass1"
}
```

---

## 未来工作计划

- 建立 Alembic 迁移，便于数据库演进
- 实现仪表盘、智能控制、聊天等模块接口
- 引入 LangGraph 工作流与 Agent 逻辑
- 增加自动化测试与 CI

---

## 变更记录与反思

- 2025-11-19：完成用户注册、登录、`/me`、退出登录接口及数据库连接。  
  - **问题**：当前缺少 Token 黑名单机制；后续需要配合 Redis 或持久化存储实现。  
  - **改进方向**：补充速率限制与审计日志，确保安全合规。

