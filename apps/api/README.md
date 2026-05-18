# Lingua API

Lingua AI 后端服务，基于 FastAPI、SQLAlchemy 和 SQLite 构建，提供登录认证、用户管理和教材管理接口。

## 技术栈

- FastAPI：HTTP API 服务与接口文档
- Uvicorn：ASGI 开发服务器
- SQLAlchemy：数据库 ORM
- SQLite：本地数据存储
- python-jose：JWT 访问令牌
- passlib + bcrypt：密码哈希
- uv：Python 依赖与运行环境管理

## 项目架构

```text
apps/api/
├── auth.py              # 密码哈希、JWT 签发与鉴权依赖
├── database.py          # SQLite 连接、Session 管理和数据目录配置
├── init_db.py           # 数据库表初始化与内置管理员创建
├── main.py              # FastAPI 应用入口、路由注册和认证接口
├── models.py            # SQLAlchemy 数据模型
├── schemas.py           # Pydantic 请求与响应模型
├── routers/
│   ├── users.py         # 用户管理接口
│   └── textbooks.py     # 教材管理接口
├── data/
│   └── lingua.db        # 本地 SQLite 数据库，启动后自动创建
├── pyproject.toml       # 项目依赖配置
└── uv.lock              # uv 锁定文件
```

### 核心模块

- `main.py`：创建 FastAPI 应用，注册 `/users` 和 `/textbooks` 路由，并提供 `/auth/login`、`/auth/me`、`/health` 等接口。
- `init_db.py`：应用启动时自动创建数据库表，并初始化内置管理员账号。
- `auth.py`：负责密码加密校验、JWT 生成、当前用户解析和管理员权限校验。
- `database.py`：配置 SQLite 数据库文件路径为 `data/lingua.db`，并提供数据库会话依赖。
- `models.py`：定义 `User`、`Textbook` 数据表和 `UserType` 用户类型枚举。
- `schemas.py`：定义登录、用户、教材等接口的请求体和响应体。

## 启动命令

进入后端目录：

```powershell
cd apps/api
```

安装依赖：

```powershell
uv sync
```


启动开发服务：

```powershell
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

也可以通过项目入口启动：

```powershell
uv run python main.py
```

服务启动后可访问：

- API 根路径：http://127.0.0.1:8000/
- 健康检查：http://127.0.0.1:8000/health
- Swagger 文档：http://127.0.0.1:8000/docs
- OpenAPI JSON：http://127.0.0.1:8000/openapi.json

## 初始账号

首次启动时会自动创建内置管理员：

```text
用户名：admin
密码：123qwe
```

## 环境变量

- `LINGUA_JWT_SECRET`：可选。用于指定 JWT 签名密钥。

如果未设置 `LINGUA_JWT_SECRET`，服务会在 `data/.jwt_secret` 中自动生成并保存一个本地密钥。

## 主要接口

- `POST /auth/login`：登录并获取访问令牌
- `GET /auth/me`：获取当前登录用户
- `GET /users`：用户列表
- `POST /users`：创建用户
- `PUT /users/{user_id}`：更新用户
- `DELETE /users/{user_id}`：删除用户
- `POST /users/{user_id}/reset-password`：重置用户密码
- `GET /textbooks`：教材列表
- `POST /textbooks`：创建教材
- `PUT /textbooks/{textbook_id}`：更新教材
- `DELETE /textbooks/{textbook_id}`：删除教材
