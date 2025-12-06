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

## 已实现功能模块

### 🔐 身份认证模块 (Authentication)

| Method | URL                | 描述           |
|--------|--------------------|----------------|
| POST   | `/api/auth/register` | 注册新用户      |
| POST   | `/api/auth/token`    | 登录并获取 Token |  
| GET    | `/api/auth/me`       | 获取当前用户信息 |
| POST   | `/api/auth/logout`   | 退出登录（前端清 Token） |

> 密码规则：长度需在 6~30 个字符之间，系统会在存储前进行截断哈希，最终加密串也不超过 30 个字符。

### 💡 智能设备管理模块 (Smart Control)

| Method | URL                              | 描述                     |
|--------|----------------------------------|--------------------------|
| POST   | `/api/appliances`                | 添加新电器                |
| GET    | `/api/appliances`                | 获取当前用户的电器列表     |
| POST   | `/api/appliances/{id}/control`   | 控制电器开关（AI 介入）    |

**功能特点:**
- 支持添加多种类型的电器（空调、冰箱、照明、电视、热水器等）
- 电器状态实时管理（开关状态）
- AI 智能建议：控制电器时会自动分析并给出节能建议（当前为模拟 AI 服务）

> 所有 `/api/appliances/*` 接口都需要先登录获取 Token，并在请求头中携带 `Authorization: Bearer <token>`

### 📊 仪表盘数据模块 (Dashboard Data)

| Method | URL                              | 描述                     |
|--------|----------------------------------|--------------------------|
| GET    | `/api/data/summary`              | 获取今日概览（KPI Cards） |
| GET    | `/api/data/consumption/trend`    | 获取用电趋势（折线图数据） |
| GET    | `/api/data/consumption/factors`   | 获取用电影响因素（AI 分析）|
| GET    | `/api/data/weather`               | 获取天气数据             |
| GET    | `/api/data/electricity-rate`     | 获取当前电价状态          |

**功能特点:**
- **今日概览**：实时计算当前总功率、今日预计电费、本月累计用电、开启电器数量
- **用电趋势**：支持 24小时/一周/一个月三种时间范围，返回格式匹配前端图表组件
- **影响因素分析**：AI 分析用电影响因素（天气、大功率电器、基础待机、峰时用电）
- **天气数据**：模拟天气信息（温度、天气状况、湿度），后续可接入真实天气 API
- **电价状态**：根据当前时间自动判断峰值/平值/谷值电价

**数据格式说明:**
- 用电趋势数据单位：**瓦特 (W)**，格式：`{data: [{time: string, usage: number}]}`
- 所有接口均需要认证（Bearer Token）

> 所有 `/api/data/*` 接口都需要先登录获取 Token，并在请求头中携带 `Authorization: Bearer <token>`

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

## 快速测试指南

### 1. 启动服务
```bash
cd backend
uvicorn app.main:app --reload
```
访问 `http://localhost:8000/docs` 查看 Swagger UI 自动生成的接口文档。

### 2. 测试流程

#### 步骤 1：注册用户
```bash
POST /api/auth/register
{
  "username": "test001",
  "password": "securePass1",
  "address": "杭州市西湖区"
}
```

#### 步骤 2：登录获取 Token
```bash
POST /api/auth/token
{
  "username": "test001",
  "password": "securePass1"
}
```
复制返回的 `access_token`。

#### 步骤 3：在 Swagger UI 中授权
点击右上角 "Authorize" 按钮，输入：`Bearer <access_token>`

#### 步骤 4：添加电器
```bash
POST /api/appliances
{
  "name": "客厅空调",
  "type": "ac",
  "power_rating": 2.5,
  "location": "Living Room"
}
```
记录返回的 `id`（例如：1）。

#### 步骤 5：查看电器列表
```bash
GET /api/appliances
```

#### 步骤 6：控制电器（体验 AI 建议）
```bash
POST /api/appliances/1/control
{
  "action": "ON"
}
```
查看返回的 `ai_message`，体验智能建议功能！

---

## 开发进度

### ✅ 已完成功能
- [x] 用户注册、登录、认证（JWT Token）
- [x] 电器数据模型（ORM）
- [x] 电器管理 API（添加、列表、控制）
- [x] 模拟 AI 服务（智能建议）
- [x] 仪表盘数据接口（用电趋势、KPI 指标、天气、电价）
- [x] 用电数据模型（ConsumptionData ORM）

### 🚧 计划中功能
- [ ] AI 聊天顾问接口
- [ ] 真实 AI Agent 集成（LangGraph）
- [ ] Alembic 数据库迁移管理
- [ ] 用电数据模拟器（定期生成真实用电数据）
- [ ] 真实天气 API 集成
- [ ] 自动化测试与 CI/CD

---

## 变更记录与反思

### 2025-01-XX：电器管理与智能控制模块
- **新增功能**：完成电器档案管理、电器列表查询、智能控制（AI 介入）
- **技术实现**：
  - 创建 `Appliance` ORM 模型，与 `User` 建立一对多关系
  - 实现 Pydantic schemas 用于请求/响应验证
  - 开发模拟 AI 服务，在控制电器时给出智能建议
  - 完成三个核心 API 端点：添加电器、查询列表、控制开关
- **文件变更**：
  - `backend/app/models/appliance.py` - 电器 ORM 模型
  - `backend/app/models/user.py` - 添加与电器的关系
  - `backend/app/schemas/appliance.py` - 电器相关的 Pydantic 模型
  - `backend/app/services/mock_ai.py` - 模拟 AI 服务
  - `backend/app/api/endpoints/appliances.py` - 电器管理 API
  - `backend/app/main.py` - 注册电器路由
- **待改进**：
  - 当前 AI 服务为模拟实现，后续需接入真实的 LangGraph Agent
  - 数据库迁移：当前使用 `Base.metadata.create_all()`，建议改用 Alembic 管理版本

### 2025-11-19：用户认证模块
- **完成功能**：用户注册、登录、`/me`、退出登录接口及数据库连接
- **问题**：当前缺少 Token 黑名单机制；后续需要配合 Redis 或持久化存储实现
- **改进方向**：补充速率限制与审计日志，确保安全合规

### 2025-12-01：数据库架构重构与用电账户管理
- **新增功能**：用电账户自动创建、峰谷电价支持、数据库关系优化
- **技术实现**：
  - 重构数据库模型，引入 `ElectricityAccount` 中间表
  - 修改注册接口，实现用户注册时自动创建用电账户
  - 优化电器与用户的关联关系：`User -> ElectricityAccount -> Appliance`
  - 支持峰谷电价配置，为未来电费计算做准备
- **文件变更**：
  - `backend/app/models/electricity_account.py` - 新增用电账户ORM模型
  - `backend/app/models/user.py` - 添加与用电账户的关系
  - `backend/app/models/appliance.py` - 修改外键关联到用电账户
  - `backend/app/api/endpoints/auth.py` - 注册时自动创建用电账户
- **架构优势**：
  - 支持复杂的电价策略（峰谷电价）
  - 为用电账单和数据分析功能预留扩展空间
  - 更好的数据隔离和关联完整性
- **数据库兼容性**：统一使用BIGINT类型，确保MySQL兼容性

### 2025-12-06：仪表盘数据接口实现与前后端联调适配
- **新增功能**：完整的仪表盘数据接口，支持前端 React 组件的数据需求
- **技术实现**：
  - 创建 `ConsumptionData` ORM 模型，支持历史用电数据存储和查询
  - 实现仪表盘数据接口，包括今日概览、用电趋势、影响因素分析、天气数据、电价状态
  - 优化数据格式，匹配前端 TypeScript 接口定义（驼峰命名、单位转换等）
  - 实现智能数据生成逻辑，当数据库无真实数据时自动生成模拟数据
- **核心文件与函数**：
  - **`backend/app/models/consumption_data.py`** - 用电数据 ORM 模型
    - `ConsumptionData` 类：对应 `consumption_data` 表，存储时间片内的总耗电量
    - 与 `ElectricityAccount` 建立一对多关系
  - **`backend/app/schemas/dashboard.py`** - 仪表盘 Pydantic 数据模型
    - `DashboardSummary`：今日概览数据模型（总功率、电费、用电量、开启电器数）
    - `ChartDataPoint`：图表数据点模型（时间、用电量）
    - `ConsumptionTrend`：用电趋势响应模型（数据点列表）
    - `ConsumptionFactors`：用电影响因素响应模型
    - `Weather`：天气数据模型（温度、天气状况、湿度）
    - `ElectricityRate`：电价状态模型（peak/normal/valley）
  - **`backend/app/api/endpoints/dashboard.py`** - 仪表盘数据接口端点
    - `get_dashboard_summary()`：获取今日概览
      - 计算当前总功率（基于开启的电器）
      - 估算今日电费（基于峰谷电价和电器使用时长）
      - 查询本月累计用电量
      - 统计开启的电器数量
    - `get_consumption_trend()`：获取用电趋势
      - 支持 24小时/一周/一个月三种时间范围
      - 优先使用数据库真实数据，无数据时生成模拟数据
      - 数据单位：瓦特 (W)，格式匹配前端 `ChartDataPoint[]`
    - `get_consumption_factors()`：获取用电影响因素
      - AI 分析天气因素、大功率电器、基础待机、峰时用电的影响权重
      - 自动归一化因子值，使总和为 100%
      - 生成智能节能建议
    - `get_weather()`：获取天气数据
      - 模拟天气信息（温度、天气状况、湿度）
      - 根据当前时间动态生成，模拟昼夜温度变化
    - `get_electricity_rate()`：获取电价状态
      - 根据当前时间自动判断峰值（18-22点）/谷值（0-7点）/平值电价
    - **辅助函数**：
      - `_calculate_current_power()`：计算当前总功率
      - `_estimate_daily_cost()`：估算今日电费
      - `_get_month_usage()`：获取本月累计用电量
      - `_generate_mock_trend_data()`：生成模拟趋势数据
- **文件变更**：
  - **新建文件**：
    - `backend/app/models/consumption_data.py` - 用电数据 ORM 模型
    - `backend/app/schemas/dashboard.py` - 仪表盘 Pydantic 模型
    - `backend/app/api/endpoints/dashboard.py` - 仪表盘数据接口
  - **修改文件**：
    - `backend/app/models/electricity_account.py` - 添加与 `ConsumptionData` 的关系
    - `backend/app/models/__init__.py` - 导出新模型（ConsumptionData, ElectricityAccount）
    - `backend/app/schemas/appliance.py` - 修改 `ApplianceOut`，`is_on` 字段使用别名 `isOn` 匹配前端
    - `backend/app/main.py` - 注册仪表盘路由（`/api/data`）
- **数据格式适配**：
  - 用电趋势接口返回格式从 `{range, x_axis, y_axis}` 改为 `{data: [{time, usage}]}`
  - 数据单位从 `kWh` 转换为 `W`（瓦特），匹配前端图表组件
  - 电器状态字段使用驼峰命名 `isOn`，匹配前端 TypeScript 接口
  - 所有时间格式统一为 `HH:MM`（24小时）或 `MM/DD`（日期）
- **前后端联调**：
  - 接口响应格式完全匹配前端 React demo 的 TypeScript 接口定义
  - 支持前端组件独立加载，避免单次请求过大
  - 提供模拟数据生成，便于前端开发和测试
- **待改进**：
  - 当前天气数据为模拟实现，后续可接入真实天气 API（如 OpenWeatherMap）
  - 用电趋势数据生成逻辑可优化，考虑接入用电数据模拟器定期写入数据库
  - 影响因素分析可接入真实 AI Agent 进行更精准的分析

