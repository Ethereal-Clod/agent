# FastAPI & SQLAlchemy 速成手册（AI 用电助手）

面向新同学的快速入门资料，包含 FastAPI/SQLAlchemy 基础概念，以及本项目中每个 Python 文件的职责与关键函数说明。

---

## 1. FastAPI 基础知识

### 1.1 创建应用与路由
- `FastAPI()`：实例化应用对象，通常放在 `app/main.py`。
- `APIRouter()`：将路由拆分成模块，再在主应用里 `include_router`。
- 装饰器：
  - `@app.get("/path")`、`@router.post("/path")` 等声明 HTTP 方法。
  - `response_model=Schema`：自动校验/序列化响应。

### 1.2 请求体验证与响应
- **Pydantic 模型**：定义请求体、响应结构，如 `UserCreate`、`UserRead`。
- 自动文档：访问 `/docs` 即可查看 Swagger UI。

### 1.3 依赖注入
- `Depends()`：FastAPI 提供的依赖系统，可注入数据库会话、当前用户等。
- 典型场景：
  - `db: Session = Depends(get_db)`
  - `current_user: User = Depends(get_current_user)`

### 1.4 中间件与跨域
- `CORSMiddleware`：允许前端（如 Vite）跨域访问，配置 `allow_origins/headers/methods`。

### 1.5 启动/热更新
```
uvicorn app.main:app --reload
```
`--reload` 会在代码变动时自动重启，适合开发环境。

---

## 2. SQLAlchemy 基础知识

### 2.1 引擎与 Session
- `create_engine(DATABASE_URL)`：建立数据库连接。
- `sessionmaker()`：创建 Session 工厂，结合 FastAPI 依赖在每个请求中获取独立会话。

### 2.2 Base 与模型
- `declarative_base()`：生成所有 ORM 模型的基类。
- 模型示例：
  ```python
  class User(Base):
      __tablename__ = "users"
      id = Column(Integer, primary_key=True)
      username = Column(String, unique=True)
  ```

### 2.3 CRUD 基本操作
- **查询**：`db.query(User).filter(User.username == name).first()`
- **创建**：`db.add(instance); db.commit(); db.refresh(instance)`
- **删除/更新**：操作实例字段后 `db.commit()`。
- 事务：一次请求默认使用单个事务，如需回滚可 `db.rollback()`。

### 2.4 SQLite vs MySQL
- SQLite 适合本地快速启动，使用 `sqlite:///./data/xxx.db`。
- MySQL 用 `mysql+pymysql://user:pwd@host:port/dbname`，配合 `db/schema.sql` 初始化表结构。

---

## 3. 项目 Python 文件速查表

| 路径 | 职责 | 关键函数/对象 |
|------|------|---------------|
| `app/main.py` | FastAPI 入口，注册路由、中间件，创建表结构。 | `app = FastAPI(...)`、`app.include_router(...)`、`@app.get("/healthz")` |
| `app/api/__init__.py` | API 包标识，便于模块化导入。 | （无） |
| `app/api/deps.py` | FastAPI 依赖集合，如解析 JWT、获取数据库会话。 | `oauth2_scheme`（OAuth2 Password Flow）、`get_current_user()` |
| `app/api/endpoints/auth.py` | 身份认证路由：注册、登录、获取当前用户、登出。 | `register_user()`、`login()`、`read_current_user()`、`logout()` |
| `app/core/config.py` | 统一配置，读取 `.env`，提供数据库/JWT/项目名等参数。 | `Settings`（继承 `BaseSettings`）、`get_settings()`、`settings` |
| `app/core/security.py` | 密码哈希与 JWT 工具。 | `verify_password()`、`get_password_hash()`、`create_access_token()`、`decode_access_token()` |
| `app/db/__init__.py` | 数据库包占位。 | （无） |
| `app/db/base.py` | SQLAlchemy `Base` 声明。 | `Base = declarative_base()` |
| `app/db/session.py` | 构建数据库引擎、Session 工厂，并提供 FastAPI 依赖。 | `_build_connect_args()`、`engine`、`SessionLocal`、`get_db()` |
| `app/models/__init__.py` | 导出 ORM 模型。 | `from .user import User`、`from .appliance import Appliance, ApplianceType` |
| `app/models/user.py` | `users` 表 ORM 模型，包含用户名、哈希密码、地址、时间戳，与电器建立一对多关系。 | `class User(Base)`、`appliances = relationship("Appliance", back_populates="owner")` |
| `app/models/appliance.py` | `appliances` 表 ORM 模型，包含电器名称、类型、开关状态、功率等，关联到用户。 | `class Appliance(Base)`、`class ApplianceType(str, enum.Enum)` |
| `app/schemas/user.py` | Pydantic 模型：通用字段、注册体、响应体、登录请求、Token。 | `UserCreate`、`UserRead`、`LoginRequest`、`Token`、`TokenData` |
| `app/schemas/appliance.py` | Pydantic 模型：创建电器、电器响应、控制请求、控制响应。 | `ApplianceCreate`、`ApplianceOut`、`ApplianceControl`、`ControlResponse` |
| `app/services/__init__.py` | 服务层包标识。 | （无） |
| `app/services/mock_ai.py` | 模拟 AI 服务，分析电器操作并返回智能建议（占位实现，后续替换为真实 Agent）。 | `analyze_appliance_action(appliance_name, action, power) -> str` |
| `app/api/endpoints/appliances.py` | 电器管理路由：添加电器、查询列表、控制开关（AI 介入）。 | `create_appliance()`、`read_appliances()`、`control_appliance()` |
| `app/test.py` | 独立示例应用/健康检查（演示性质）。 | `app = FastAPI(...)`、`@app.get("/")` |

> 提示：添加新模块时，可沿用“模型（models）+模式（schemas）+路由（api/endpoints）+依赖（api/deps）”的结构，保持一致的代码组织方式。

---

## 4. 编写/扩展模块的小贴士

1. **定义请求/响应模型**（`schemas/`）→ 保证数据结构清晰。
2. **实现 ORM 模型**（`models/`）→ 与数据库字段对应。
3. **编写业务路由**（`api/endpoints/`）→ 使用依赖注入拿到 `db`、`current_user`。
4. **更新文档**（`README.md` 或本手册）→ 方便团队成员快速理解。
5. **测试接口**：优先通过 `/docs`、`curl` 或 Postman 自检，再交付给前端。

> 密码策略：长度 6~30 个字符，注册/登录时都会校验；内部使用 SHA-256 后截取 30 个字符存储，因此数据库 `users.password` 字段为 `VARCHAR(30)`。

---

## 5. 新增模块：电器管理与智能控制

### 5.1 数据模型设计

**Appliance 模型** (`app/models/appliance.py`)
- 与 `User` 建立多对一关系（一个用户可以有多个电器）
- 使用 `ApplianceType` 枚举定义电器类型（ac、fridge、light、tv、heater、other）
- 关键字段：`name`（名称）、`type`（类型）、`is_on`（开关状态）、`power_rating_kw`（功率）

**关系定义**
```python
# User 模型中添加
appliances = relationship("Appliance", back_populates="owner")

# Appliance 模型中添加
user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
owner = relationship("User", back_populates="appliances")
```

### 5.2 API 端点说明

**`POST /api/appliances`** - 添加新电器
- 功能：创建电器记录，绑定到当前登录用户
- 依赖：`get_current_user`（确保用户已登录）
- 返回：创建的电器信息（`ApplianceOut`）

**`GET /api/appliances`** - 获取电器列表
- 功能：查询当前用户的所有电器
- 筛选：自动过滤，只返回属于当前用户的电器
- 返回：电器列表（`List[ApplianceOut]`）

**`POST /api/appliances/{appliance_id}/control`** - 控制电器开关
- 功能：更新电器开关状态，并调用 AI 服务分析
- 流程：
  1. 验证电器存在且属于当前用户
  2. 更新 `is_on` 状态
  3. 调用 `analyze_appliance_action()` 获取 AI 建议
  4. 提交事务并返回结果
- 返回：控制结果 + AI 建议消息（`ControlResponse`）

### 5.3 模拟 AI 服务

**`app/services/mock_ai.py`** 中的 `analyze_appliance_action()` 函数：
- 输入：电器名称、操作类型（"ON"/"OFF"）、功率
- 逻辑：
  - 关闭操作：返回节能提示
  - 开启操作：随机选择一个智能建议（如高峰提示、温度建议等）
- 后续：此函数将被替换为真实的 LangGraph Agent 调用

### 5.4 开发流程总结

实现新模块的标准流程：
1. **定义 ORM 模型** (`models/`) → 数据库表结构
2. **定义 Pydantic schemas** (`schemas/`) → 请求/响应验证
3. **编写业务逻辑** (`services/`) → 核心算法或 AI 调用
4. **创建 API 端点** (`api/endpoints/`) → HTTP 接口
5. **注册路由** (`main.py`) → 让 FastAPI 识别新接口
6. **更新文档** → API 文档、README、本手册

---

这份手册会随着后续模块（仪表盘、真实 AI Agent、聊天）的实现不断扩充。遇到新的基础概念，也请在这里补充，便于后来者快速融入。


