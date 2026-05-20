# Chatbox-Private 私域 Chatbot 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `cxy-suban-lingxi/lingxi` 前端独立为一个仅 H5 的对话产品，配套一个轻量 FastAPI 适配后端，接入 OpenAI 兼容的私有大模型（qwen3-32b @ 188.109.35.147:9092），通过 Docker Compose 在私域内网一键部署。

**Architecture:**
- 单仓库三组件：`frontend/`（uni-app H5 静态产物）+ `backend/`（FastAPI + SQLite）+ `docker-compose.yml`。
- 入口为 nginx 容器，`/` 托管前端静态资源、`/api/*` 反向代理到 backend；backend 内部不对外暴露。
- 后端职责：会话/消息/文件 CRUD（SQLite）；把前端的 multipart + SSE 契约转换为上游 OpenAI 兼容流式调用并回传 SSE 帧；多模态内容结构存库以便后续无痛切换多模态模型。
- 会话以 `X-Client-Id`（浏览器 localStorage 生成的 UUID）做匿名隔离。

**Tech Stack:**
- 前端：Vue 3 + uni-app + TypeScript + Vite + Pinia + Tailwind + markdown-it（沿用 lingxi 现有栈，只跑 `build:h5`）
- 后端：Python 3.11 + FastAPI + Uvicorn + SQLAlchemy 2.x + SQLite（WAL）+ httpx (async) + pypdf + python-docx + pydantic-settings + pytest
- 部署：Docker + Docker Compose + nginx 1.25-alpine
- 规范：遵循 `cxy-suban-lingxi/docs/reference/` 下 fastapi / deployment / sqlite / testing-and-logging 最佳实践

**参考与上下文：**
- 旧前端源：`/Users/jia/MyProjects/pythonProjects/cmcc_cxy/Bprocss/cxy-suban-lingxi/lingxi/`
- 关键改造点：`lingxi/src/stores/modules/chat.ts`（SSE 处理 + 5 个 URL）、`lingxi/src/utils/http.ts`（拦截器与 BASE_URL）、`lingxi/.env`、`lingxi/vite.config.ts`、`lingxi/src/pages/network-agent/components/Message/message_item.vue`
- 上游 LLM：`POST http://188.109.35.147:9092/v1/chat/completions`，body `{model: "qwen3-32b", stream: true, max_tokens, messages}`，无鉴权
- 工作目录（新建独立 git 仓库）：`/Users/jia/MyProjects/pythonProjects/cmcc_cxy/Bprocss/chatbox-private/`

---

## 文件结构总览

完成态目录树：

```
chatbox-private/                       (独立 git 仓库)
├── .gitignore
├── .env.example                       # docker-compose 用的环境模板
├── README.md
├── PLAN.md                            # 本文档
├── docker-compose.yml
├── docs/
│   ├── architecture.md                # 架构 + 数据流 + SSE 协议
│   ├── deployment.md                  # 部署手册（含离线镜像）
│   ├── usage.md                       # 用户与开发者使用指南
│   └── api.md                         # 后端 API 契约
├── nginx/
│   └── default.conf                   # Web 容器内 nginx 配置
├── scripts/
│   └── offline-bundle.sh              # 打包离线镜像
├── frontend/
│   ├── package.json
│   ├── pnpm-lock.yaml                 # 拷自 lingxi/
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── .env.development
│   ├── .env.production
│   ├── Dockerfile                     # multi-stage: node build → nginx serve
│   ├── nginx.conf                     # 容器内 web 服务配置
│   └── src/                           # 从 lingxi/src 拷贝并裁剪
│       ├── main.ts
│       ├── App.vue
│       ├── pages.json
│       ├── manifest.json
│       ├── env.d.ts
│       ├── stores/                    # 仅保留 chat / session
│       ├── pages/network-agent/       # 仅保留 H5 路径相关
│       ├── components/
│       ├── utils/
│       │   ├── http.ts                # 改造：BASE_URL + X-Client-Id
│       │   ├── client_id.ts           # 新增：localStorage 维护 client_id
│       │   └── markdownLink.ts
│       ├── style/
│       ├── static/
│       ├── assets/
│       └── types/
└── backend/
    ├── pyproject.toml
    ├── requirements.txt
    ├── .env.example
    ├── Dockerfile
    ├── alembic.ini                    # 暂未启用（M5 才接 alembic，可选）
    ├── src/
    │   ├── __init__.py
    │   ├── main.py                    # FastAPI app + lifespan + 路由挂载
    │   ├── config.py                  # pydantic-settings
    │   ├── database.py                # engine + SessionLocal + get_db
    │   ├── logging_setup.py           # JSON 行日志到 stdout
    │   ├── shared/
    │   │   ├── __init__.py
    │   │   ├── exceptions.py          # AppException + 注册全局处理
    │   │   ├── sse.py                 # SSE 帧编码器
    │   │   └── client_id.py           # X-Client-Id 依赖
    │   ├── chat/
    │   │   ├── __init__.py
    │   │   ├── router.py              # POST /api/v1/chat/stream
    │   │   ├── schemas.py
    │   │   ├── llm_client.py          # 上游 OpenAI 兼容客户端
    │   │   └── service.py             # 协议转换 + 落库
    │   ├── sessions/
    │   │   ├── __init__.py
    │   │   ├── router.py              # /api/v1/sessions
    │   │   ├── models.py              # SQLAlchemy Session / Message
    │   │   ├── schemas.py
    │   │   └── service.py
    │   ├── files/
    │   │   ├── __init__.py
    │   │   ├── router.py              # /api/v1/files + 静态下载
    │   │   ├── models.py              # File 模型
    │   │   ├── schemas.py
    │   │   ├── service.py
    │   │   └── extractor.py           # pdf/docx/txt 抽文本
    │   └── compat/
    │       ├── __init__.py
    │       └── router.py              # scene/use + duration 占位
    └── tests/
        ├── __init__.py
        ├── conftest.py
        ├── test_health.py
        ├── test_chat.py
        ├── test_sessions.py
        └── test_files.py
```

---

# 里程碑划分

- **M1 脚手架**：仓库 + 前端拷贝（H5 跑通空白页）+ 后端骨架 + 一键 compose 起服务，`/api/v1/health` 通。
- **M2 对话联通**：SSE 协议转换 + 上游 LLM 调通，前端能完成一次对话。
- **M3 会话持久化**：SQLite + Sessions CRUD + client_id 隔离，侧边栏可用。
- **M4 文件上传**：多模态内容结构 + pdf/docx/txt 抽取 + 前端附件渲染。
- **M5 打磨**：兼容端点、日志、错误处理、文档全套、离线镜像脚本。

每个里程碑结束打 tag `v0.1.0-m{N}`。

---

# Milestone 1：脚手架

### Task 1.1：初始化仓库与顶层文件

**Files:**
- Create: `chatbox-private/.gitignore`
- Create: `chatbox-private/README.md`
- Create: `chatbox-private/.env.example`

- [ ] **Step 1: 初始化 git 仓库**

Run:
```bash
cd /Users/jia/MyProjects/pythonProjects/cmcc_cxy/Bprocss/chatbox-private
git init
git checkout -b main
```
Expected: `Initialized empty Git repository ...`

- [ ] **Step 2: 写 .gitignore**

Create `chatbox-private/.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
.pytest_cache/
.mypy_cache/

# Node
node_modules/
dist/
.unpackage/
.parcel-cache/

# IDE / OS
.idea/
.vscode/
.DS_Store

# Env
.env
.env.local
*.local

# Runtime data
data/db/*.sqlite*
data/uploads/*
!data/db/.gitkeep
!data/uploads/.gitkeep

# Logs
*.log
logs/
```

- [ ] **Step 3: 写 README.md**

Create `chatbox-private/README.md`:

````markdown
# chatbox-private

私域内网部署的对话式 AI 应用，前端从 lingxi 迁移并精简为 H5；后端为 FastAPI 适配层，接入 OpenAI 兼容的私有大模型。

## 一键启动

```bash
cp .env.example .env
# 编辑 .env，按需修改 LLM_BASE_URL、LLM_MODEL
docker compose up -d --build
```

浏览器访问 http://localhost:8080

## 目录

- `frontend/`：Vue3 + uni-app H5
- `backend/`：FastAPI 适配后端
- `nginx/`：网关配置（如需独立网关层）
- `docs/`：架构 / 部署 / 使用 / API 文档
- `data/`：运行时数据卷（SQLite 与上传文件）

## 文档

- 架构：[docs/architecture.md](docs/architecture.md)
- 部署：[docs/deployment.md](docs/deployment.md)
- 使用：[docs/usage.md](docs/usage.md)
- API：[docs/api.md](docs/api.md)
````

- [ ] **Step 4: 写 .env.example**

Create `chatbox-private/.env.example`:

```env
# Public web port (host side)
WEB_PORT=8080

# Upstream LLM (OpenAI compatible)
LLM_BASE_URL=http://188.109.35.147:9092/v1
LLM_MODEL=qwen3-32b
LLM_MAX_TOKENS=32000
LLM_API_KEY=
LLM_TIMEOUT_SECONDS=300

# Backend
BACKEND_LOG_LEVEL=INFO
```

- [ ] **Step 5: 占位数据目录**

Run:
```bash
mkdir -p data/db data/uploads
touch data/db/.gitkeep data/uploads/.gitkeep
```

- [ ] **Step 6: 首次提交**

```bash
git add .gitignore README.md .env.example data/db/.gitkeep data/uploads/.gitkeep PLAN.md
git commit -m "chore: bootstrap chatbox-private repo"
```

---

### Task 1.2：后端骨架（FastAPI + 配置 + health）

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/src/__init__.py`
- Create: `backend/src/config.py`
- Create: `backend/src/main.py`
- Create: `backend/src/logging_setup.py`

- [ ] **Step 1: 写 requirements.txt**

Create `backend/requirements.txt`:

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
pydantic-settings==2.5.2
sqlalchemy==2.0.34
httpx==0.27.2
python-multipart==0.0.9
pypdf==5.0.1
python-docx==1.1.2
aiofiles==24.1.0
```

- [ ] **Step 2: 写 pyproject.toml（最小，仅用于工具）**

Create `backend/pyproject.toml`:

```toml
[project]
name = "chatbox-backend"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 3: 写 backend/.env.example**

Create `backend/.env.example`:

```env
LLM_BASE_URL=http://188.109.35.147:9092/v1
LLM_MODEL=qwen3-32b
LLM_MAX_TOKENS=32000
LLM_API_KEY=
LLM_TIMEOUT_SECONDS=300
DB_URL=sqlite:///./data/db/chatbox.sqlite
UPLOAD_DIR=./data/uploads
LOG_LEVEL=INFO
CORS_ORIGINS=["*"]
```

- [ ] **Step 4: 写 config.py**

Create `backend/src/__init__.py` (空文件)

Create `backend/src/config.py`:

```python
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_base_url: str = "http://188.109.35.147:9092/v1"
    llm_model: str = "qwen3-32b"
    llm_max_tokens: int = 32000
    llm_api_key: str = ""
    llm_timeout_seconds: int = 300

    db_url: str = "sqlite:///./data/db/chatbox.sqlite"
    upload_dir: str = "./data/uploads"

    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 5: 写 logging_setup.py**

Create `backend/src/logging_setup.py`:

```python
import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
```

- [ ] **Step 6: 写 main.py（含 health）**

Create `backend/src/main.py`:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.logging_setup import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="chatbox-backend", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    health = APIRouter(prefix="/api/v1", tags=["health"])

    @health.get("/health")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(health)
    return app


app = create_app()
```

- [ ] **Step 7: 本地起服务验证**

Run:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/api/v1/health
kill %1
```
Expected: `{"status":"ok"}`

- [ ] **Step 8: 提交**

```bash
cd /Users/jia/MyProjects/pythonProjects/cmcc_cxy/Bprocss/chatbox-private
git add backend/
git commit -m "feat(backend): scaffold FastAPI app with health endpoint"
```

---

### Task 1.3：后端单测脚手架 + health 测试

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_health.py`
- Modify: `backend/requirements.txt` 追加测试依赖

- [ ] **Step 1: 追加测试依赖**

Edit `backend/requirements.txt` 末尾追加：

```txt
pytest==8.3.3
pytest-asyncio==0.24.0
```

Run:
```bash
cd backend && source .venv/bin/activate && pip install -r requirements.txt
```

- [ ] **Step 2: 写 conftest.py**

Create `backend/tests/__init__.py` (空)

Create `backend/tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    return TestClient(app)
```

- [ ] **Step 3: 写 failing test**

Create `backend/tests/test_health.py`:

```python
def test_health_returns_ok(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

- [ ] **Step 4: 运行测试**

Run:
```bash
cd backend && source .venv/bin/activate && pytest -v
```
Expected: 1 passed

- [ ] **Step 5: 提交**

```bash
git add backend/tests/ backend/requirements.txt
git commit -m "test(backend): add health endpoint test"
```

---

### Task 1.4：从 lingxi 迁移前端源到 frontend/

**Files:**
- Create: `frontend/*` (从 `cxy-suban-lingxi/lingxi/` 拷贝)
- Modify: `frontend/package.json`（精简 scripts 与依赖）
- Modify: `frontend/.env.development` / `.env.production`
- Modify: `frontend/vite.config.ts`

- [ ] **Step 1: 拷贝源码**

Run:
```bash
cd /Users/jia/MyProjects/pythonProjects/cmcc_cxy/Bprocss/chatbox-private
LX=/Users/jia/MyProjects/pythonProjects/cmcc_cxy/Bprocss/cxy-suban-lingxi/lingxi
mkdir -p frontend
cp -R "$LX/src" frontend/src
cp "$LX/index.html" frontend/index.html
cp "$LX/vite.config.ts" frontend/vite.config.ts
cp "$LX/tsconfig.json" frontend/tsconfig.json
cp "$LX/tailwind.config.js" frontend/tailwind.config.js
cp "$LX/postcss.config.js" frontend/postcss.config.js
cp "$LX/package.json" frontend/package.json
cp "$LX/pnpm-lock.yaml" frontend/pnpm-lock.yaml
cp "$LX/shims-uni.d.ts" frontend/shims-uni.d.ts
cp "$LX/favicon.ico" frontend/favicon.ico 2>/dev/null || true
```

- [ ] **Step 2: 精简 package.json scripts，只保留 H5**

Edit `frontend/package.json` 的 `scripts` 字段替换为：

```json
{
  "scripts": {
    "dev": "uni",
    "build": "uni build",
    "type-check": "vue-tsc --noEmit"
  }
}
```

依赖部分**保留 vue/uni-app/uni-h5/uni-components/uni-ui/uni-cli-shared/vite-plugin-uni/types/automator/stacktracey 等核心依赖**，删除以下小程序专属：`@dcloudio/uni-mp-*`、`@dcloudio/uni-quickapp-*`、`@dcloudio/uni-app-plus`、`@dcloudio/uni-app-harmony`、`@dcloudio/uni-mp-harmony`、`weapp-tailwindcss`。

最终 `frontend/package.json` 完整内容：

```json
{
  "name": "chatbox-frontend",
  "version": "0.1.0",
  "scripts": {
    "dev": "uni",
    "build": "uni build",
    "type-check": "vue-tsc --noEmit"
  },
  "dependencies": {
    "@dcloudio/uni-app": "3.0.0-4080420251103001",
    "@dcloudio/uni-components": "3.0.0-4080420251103001",
    "@dcloudio/uni-h5": "3.0.0-4080420251103001",
    "@dcloudio/uni-ui": "1.4.20",
    "@vscode/markdown-it-katex": "^1.1.2",
    "autoprefixer": "^10.4.23",
    "crypto-js": "4.2.0",
    "dayjs": "^1.11.20",
    "echarts": "^6.0.0",
    "entities": "^7.0.1",
    "highcharts": "^12.5.0",
    "highlight.js": "^11.11.1",
    "katex": "^0.16.28",
    "linkify-it": "^5.0.0",
    "markdown-it": "^14.1.0",
    "markdown-it-link-attributes": "^4.0.1",
    "mdurl": "^2.0.0",
    "mermaid": "^11.12.2",
    "mermaid-it-markdown": "^1.0.13",
    "pinia": "2.3.1",
    "pinia-plugin-persistedstate": "3.2.3",
    "punycode.js": "^2.3.1",
    "uc.micro": "^2.1.0",
    "uuid": "11.1.0",
    "vue": "^3.4.21",
    "vue-echarts": "^8.0.1",
    "vue-i18n": "^9.1.9"
  },
  "devDependencies": {
    "@dcloudio/types": "^3.4.8",
    "@dcloudio/uni-cli-shared": "3.0.0-4080420251103001",
    "@dcloudio/vite-plugin-uni": "3.0.0-4080420251103001",
    "@types/markdown-it": "^14.1.2",
    "@types/markdown-it-link-attributes": "^3.0.5",
    "@vue/runtime-core": "^3.4.21",
    "@vue/tsconfig": "^0.1.3",
    "sass": "1.89.1",
    "tailwindcss": "3.4.19",
    "typescript": "^4.9.4",
    "vite": "5.2.8",
    "vue-tsc": "^1.0.24"
  }
}
```

- [ ] **Step 3: 改 vite.config.ts，去掉 weapp 插件 + 调整代理**

Replace `frontend/vite.config.ts` 内容为：

```ts
import { defineConfig, loadEnv } from 'vite'
import path from 'path'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig(({ mode }) => {
  const viteEnv = loadEnv(mode, process.cwd())
  return {
    resolve: {
      alias: {
        '@': `${path.resolve(__dirname, 'src')}`
      }
    },
    build: {
      sourcemap: process.env.NODE_ENV === 'development'
    },
    plugins: [uni()],
    server: {
      host: true,
      port: 8080,
      hmr: true,
      open: false,
      cors: true,
      proxy: {
        '/api': {
          target: viteEnv.VITE_BACKEND_URL || 'http://localhost:8000',
          changeOrigin: true
        },
        '/files': {
          target: viteEnv.VITE_BACKEND_URL || 'http://localhost:8000',
          changeOrigin: true
        }
      }
    },
    css: {
      postcss: {
        plugins: [require('tailwindcss'), require('autoprefixer')]
      }
    }
  }
})
```

- [ ] **Step 4: 写两份 env**

Create `frontend/.env.development`:

```env
VITE_APP_BASE_API=/api/v1
VITE_BACKEND_URL=http://localhost:8000
```

Create `frontend/.env.production`:

```env
VITE_APP_BASE_API=/api/v1
```

- [ ] **Step 5: 删 manifest.json 里非 H5 平台配置**

Open `frontend/src/manifest.json`，把 `mp-weixin`、`mp-alipay`、`app-plus`、`quickapp` 等顶层 key 删除（保留 `name`、`appid`、`description`、`versionName`、`versionCode`、`h5`、`vueVersion`）。**保留** `h5` 节点。如果原文件中 `h5` 节点缺失，补：

```json
{
  "h5": {
    "router": {
      "mode": "hash",
      "base": "/"
    },
    "title": "ChatBox"
  }
}
```

- [ ] **Step 6: 删除多余的 store 与无关组件**

Run:
```bash
cd /Users/jia/MyProjects/pythonProjects/cmcc_cxy/Bprocss/chatbox-private/frontend/src
rm -f stores/modules/member.ts
# session.ts、chat.ts 保留（M2/M3 改造）
```

如果 `App.vue` 或 `main.ts` 中有 `useMemberStore` 引用，注释掉相关行（M2 任务再彻底改）。

- [ ] **Step 7: 安装并构建验证**

Run:
```bash
cd frontend
pnpm install
pnpm build
ls -la dist/build/h5/index.html
```
Expected: `dist/build/h5/index.html` 存在。
若 pnpm 不可用，回退 `npm install --legacy-peer-deps && npm run build`。

- [ ] **Step 8: 提交**

```bash
cd /Users/jia/MyProjects/pythonProjects/cmcc_cxy/Bprocss/chatbox-private
git add frontend/
git commit -m "feat(frontend): migrate lingxi sources, trim to H5 only"
```

---

### Task 1.5：前端 Dockerfile + nginx 配置

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/nginx.conf`

- [ ] **Step 1: 写 Dockerfile**

Create `frontend/Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1
ARG NPM_REGISTRY=https://registry.npmmirror.com

FROM node:18-alpine AS builder
WORKDIR /app
ARG NPM_REGISTRY
RUN corepack enable && npm config set registry "$NPM_REGISTRY"
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM nginx:1.25-alpine
COPY --from=builder /app/dist/build/h5 /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

- [ ] **Step 2: 写 nginx.conf**

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;
    client_max_body_size 50m;

    root /usr/share/nginx/html;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API（同源代理）
    location /api/ {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # SSE
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        chunked_transfer_encoding on;
    }

    # 上传文件直链
    location /files/ {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_read_timeout 120s;
    }
}
```

- [ ] **Step 3: 提交**

```bash
git add frontend/Dockerfile frontend/nginx.conf
git commit -m "feat(frontend): Dockerfile and nginx config for H5 + API proxy"
```

---

### Task 1.6：后端 Dockerfile

**Files:**
- Create: `backend/Dockerfile`

- [ ] **Step 1: 写 Dockerfile**

Create `backend/Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
ARG PIP_INDEX_URL
RUN pip config set global.index-url "$PIP_INDEX_URL"
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
RUN mkdir -p /data/db /data/uploads
ENV DB_URL=sqlite:////data/db/chatbox.sqlite \
    UPLOAD_DIR=/data/uploads
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: 本地构建一次**

Run:
```bash
cd backend && docker build -t chatbox-backend:dev .
```
Expected: build success；末尾出现 `naming to docker.io/library/chatbox-backend:dev`

- [ ] **Step 3: 提交**

```bash
cd .. && git add backend/Dockerfile
git commit -m "feat(backend): Dockerfile"
```

---

### Task 1.7：docker-compose 一键拉起 + 烟测

**Files:**
- Create: `chatbox-private/docker-compose.yml`

- [ ] **Step 1: 写 docker-compose.yml**

Create `chatbox-private/docker-compose.yml`:

```yaml
services:
  api:
    build:
      context: ./backend
    environment:
      - LLM_BASE_URL=${LLM_BASE_URL}
      - LLM_MODEL=${LLM_MODEL}
      - LLM_MAX_TOKENS=${LLM_MAX_TOKENS}
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_TIMEOUT_SECONDS=${LLM_TIMEOUT_SECONDS}
      - LOG_LEVEL=${BACKEND_LOG_LEVEL}
    volumes:
      - ./data/db:/data/db
      - ./data/uploads:/data/uploads
    restart: unless-stopped
    networks: [internal]

  web:
    build:
      context: ./frontend
    ports:
      - "${WEB_PORT}:80"
    depends_on:
      - api
    restart: unless-stopped
    networks: [internal]

networks:
  internal:
    driver: bridge
```

- [ ] **Step 2: 拷 .env**

Run:
```bash
cp .env.example .env
```

- [ ] **Step 3: 起服务**

Run:
```bash
docker compose up -d --build
sleep 5
curl -s http://localhost:8080/api/v1/health
```
Expected: `{"status":"ok"}`

浏览器访问 `http://localhost:8080`，看到 lingxi 现有界面（接口可能报错，符合预期，M2 会修）。

- [ ] **Step 4: 提交并打 tag**

```bash
docker compose down
git add docker-compose.yml
git commit -m "chore: docker-compose with web + api services"
git tag v0.1.0-m1
```

---

# Milestone 2：对话联通

### Task 2.1：SSE 帧编码器（含失败测试先行）

**Files:**
- Create: `backend/src/shared/__init__.py`
- Create: `backend/src/shared/sse.py`
- Create: `backend/tests/test_sse.py`

- [ ] **Step 1: 写 failing test**

Create `backend/src/shared/__init__.py` (空)

Create `backend/tests/test_sse.py`:

```python
import json
from src.shared.sse import sse_text_chunk, sse_done


def test_sse_text_chunk_format():
    line = sse_text_chunk("hello")
    assert line.startswith("data: ")
    assert line.endswith("\n\n")
    payload = json.loads(line[len("data: "):].strip())
    assert payload["code"] == "00000"
    assert payload["choices"][0]["type"] == "markdown"
    assert payload["choices"][0]["message"]["content"] == "hello"


def test_sse_done_frame():
    line = sse_done()
    payload = json.loads(line[len("data: "):].strip())
    assert payload["choices"][0]["finish_reason"] == "stop"
```

- [ ] **Step 2: 运行测试确认失败**

Run:
```bash
cd backend && source .venv/bin/activate && pytest tests/test_sse.py -v
```
Expected: ImportError 或 ModuleNotFoundError

- [ ] **Step 3: 实现 sse.py**

Create `backend/src/shared/sse.py`:

```python
import json
from typing import Any


def _frame(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def sse_text_chunk(content: str, msg_type: str = "markdown") -> str:
    return _frame({
        "code": "00000",
        "choices": [{
            "type": msg_type,
            "message": {"content": content},
        }],
    })


def sse_done() -> str:
    return _frame({
        "code": "00000",
        "choices": [{"finish_reason": "stop"}],
    })


def sse_error(message: str, code: str = "10000") -> str:
    return _frame({"code": code, "message": message, "choices": []})
```

- [ ] **Step 4: 运行测试通过**

Run: `pytest tests/test_sse.py -v`
Expected: 2 passed

- [ ] **Step 5: 提交**

```bash
git add backend/src/shared/ backend/tests/test_sse.py
git commit -m "feat(backend): SSE frame encoder"
```

---

### Task 2.2：上游 LLM 客户端（httpx async 流式）

**Files:**
- Create: `backend/src/chat/__init__.py`
- Create: `backend/src/chat/llm_client.py`
- Create: `backend/tests/test_llm_client.py`

- [ ] **Step 1: 写 failing test（用 respx 模拟，避免依赖远端）**

追加测试依赖到 `backend/requirements.txt`:

```txt
respx==0.21.1
```

Run: `pip install respx==0.21.1`

Create `backend/src/chat/__init__.py` (空)

Create `backend/tests/test_llm_client.py`:

```python
import httpx
import pytest
import respx

from src.chat.llm_client import LLMClient


@pytest.mark.asyncio
async def test_stream_yields_delta_contents():
    base = "http://fake-llm/v1"
    body = (
        'data: {"choices":[{"delta":{"content":"你好"}}]}\n\n'
        'data: {"choices":[{"delta":{"content":"，世界"}}]}\n\n'
        'data: [DONE]\n\n'
    )
    with respx.mock(assert_all_called=True) as r:
        r.post(f"{base}/chat/completions").mock(
            return_value=httpx.Response(200, text=body, headers={"content-type": "text/event-stream"})
        )
        client = LLMClient(base_url=base, model="qwen3-32b", api_key="", max_tokens=128, timeout=30)
        out: list[str] = []
        async for chunk in client.stream([{"role": "user", "content": "hi"}]):
            out.append(chunk)
        await client.aclose()
    assert "".join(out) == "你好，世界"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest tests/test_llm_client.py -v`
Expected: ModuleNotFoundError

- [ ] **Step 3: 实现 llm_client.py**

Create `backend/src/chat/llm_client.py`:

```python
import json
import logging
from typing import AsyncIterator

import httpx

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str,
        max_tokens: int,
        timeout: int,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._max_tokens = max_tokens
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=httpx.Timeout(timeout, connect=10),
        )

    async def stream(self, messages: list[dict]) -> AsyncIterator[str]:
        payload = {
            "model": self._model,
            "stream": True,
            "max_tokens": self._max_tokens,
            "messages": messages,
        }
        async with self._client.stream("POST", "/chat/completions", json=payload) as resp:
            if resp.status_code >= 400:
                detail = await resp.aread()
                raise RuntimeError(f"upstream {resp.status_code}: {detail!r}")
            async for raw in resp.aiter_lines():
                if not raw:
                    continue
                if not raw.startswith("data:"):
                    continue
                data = raw[len("data:"):].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    logger.warning("bad upstream chunk: %s", data)
                    continue
                choices = obj.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                content = delta.get("content")
                if content:
                    yield content

    async def aclose(self) -> None:
        await self._client.aclose()
```

- [ ] **Step 4: 运行测试通过**

Run: `pytest tests/test_llm_client.py -v`
Expected: 1 passed

- [ ] **Step 5: 提交**

```bash
git add backend/src/chat/__init__.py backend/src/chat/llm_client.py \
        backend/tests/test_llm_client.py backend/requirements.txt
git commit -m "feat(backend): async streaming LLM client"
```

---

### Task 2.3：Chat schemas

**Files:**
- Create: `backend/src/chat/schemas.py`

- [ ] **Step 1: 写 schemas.py**

Create `backend/src/chat/schemas.py`:

```python
from typing import Literal, Union
from pydantic import BaseModel, Field


class TextPart(BaseModel):
    type: Literal["text"]
    text: str


class FilePart(BaseModel):
    type: Literal["file"]
    file: dict  # {file_id, name, url}


class ImagePart(BaseModel):
    type: Literal["image_url"]
    image_url: dict  # {url}


ContentPart = Union[TextPart, FilePart, ImagePart]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: Union[str, list[ContentPart]]


class ChatRequest(BaseModel):
    sessionId: str
    messageId: str
    messages: list[ChatMessage] = Field(default_factory=list)
    think: bool = False
    stream: bool = True
    file_ids: list[str] = Field(default_factory=list)
```

- [ ] **Step 2: 提交**

```bash
git add backend/src/chat/schemas.py
git commit -m "feat(backend): chat request/message schemas"
```

---

### Task 2.4：Chat service（协议转换）

**Files:**
- Create: `backend/src/chat/service.py`
- Create: `backend/tests/test_chat_service.py`

- [ ] **Step 1: 写 failing test**

Create `backend/tests/test_chat_service.py`:

```python
import pytest

from src.chat.service import flatten_for_upstream
from src.chat.schemas import ChatMessage


def test_flatten_string_content():
    out = flatten_for_upstream([
        ChatMessage(role="user", content="你好"),
        ChatMessage(role="assistant", content="你好啊"),
    ])
    assert out == [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好啊"},
    ]


def test_flatten_multimodal_text_only():
    msg = ChatMessage(role="user", content=[
        {"type": "text", "text": "总结一下"},
        {"type": "file", "file": {"file_id": "f1", "name": "a.txt", "url": "/files/f1"}},
    ])
    out = flatten_for_upstream([msg], file_texts={"f1": "这是文件内容"})
    assert out[0]["role"] == "user"
    assert "总结一下" in out[0]["content"]
    assert "这是文件内容" in out[0]["content"]
    assert "a.txt" in out[0]["content"]
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest tests/test_chat_service.py -v`
Expected: ModuleNotFoundError on `src.chat.service`

- [ ] **Step 3: 实现 service.py**

Create `backend/src/chat/service.py`:

```python
from typing import Iterable
from src.chat.schemas import ChatMessage


def flatten_for_upstream(
    messages: list[ChatMessage],
    *,
    file_texts: dict[str, str] | None = None,
) -> list[dict]:
    """把多模态 parts 数组扁平化为上游模型期望的纯文本 content。
    file_texts: file_id -> 抽取出的纯文本。"""
    file_texts = file_texts or {}
    flat: list[dict] = []
    for m in messages:
        if isinstance(m.content, str):
            flat.append({"role": m.role, "content": m.content})
            continue
        text_buf: list[str] = []
        for part in m.content:
            ptype = part.type if hasattr(part, "type") else part.get("type")
            if ptype == "text":
                text_buf.append(part.text if hasattr(part, "text") else part.get("text", ""))
            elif ptype == "file":
                fobj = part.file if hasattr(part, "file") else part.get("file", {})
                name = fobj.get("name", "attachment")
                fid = fobj.get("file_id", "")
                extra = file_texts.get(fid, "")
                if extra:
                    text_buf.append(f"\n\n---\n附件「{name}」内容：\n{extra}")
                else:
                    text_buf.append(f"\n\n[附件：{name}]")
            elif ptype == "image_url":
                text_buf.append("\n\n[图片附件，当前模型暂不支持图像理解]")
        flat.append({"role": m.role, "content": "".join(text_buf).strip()})
    return flat
```

- [ ] **Step 4: 运行测试通过**

Run: `pytest tests/test_chat_service.py -v`
Expected: 2 passed

- [ ] **Step 5: 提交**

```bash
git add backend/src/chat/service.py backend/tests/test_chat_service.py
git commit -m "feat(backend): flatten multimodal content for upstream"
```

---

### Task 2.5：Chat router `/api/v1/chat/stream`（M2 版：无文件、无落库）

**Files:**
- Create: `backend/src/chat/router.py`
- Modify: `backend/src/main.py`
- Create: `backend/tests/test_chat_stream.py`

- [ ] **Step 1: 写 failing test**

Create `backend/tests/test_chat_stream.py`:

```python
import json
import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture()
def app():
    return create_app()


def test_chat_stream_basic(app, monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://fake-llm/v1")
    monkeypatch.setenv("LLM_MODEL", "qwen3-32b")
    # 重新构造 app 让 settings 重新加载
    from src.config import get_settings
    get_settings.cache_clear()

    body = (
        'data: {"choices":[{"delta":{"content":"你好"}}]}\n\n'
        'data: [DONE]\n\n'
    )
    with respx.mock() as r:
        r.post("http://fake-llm/v1/chat/completions").mock(
            return_value=httpx.Response(200, text=body)
        )
        client = TestClient(create_app())
        # multipart: 仅 data 字段
        payload = {
            "sessionId": "s1",
            "messageId": "m1",
            "messages": [{"role": "user", "content": "hi"}],
            "think": False,
            "stream": True,
        }
        with client.stream(
            "POST",
            "/api/v1/chat/stream",
            files={"data": ("data.json", json.dumps(payload), "application/json")},
        ) as resp:
            assert resp.status_code == 200
            chunks = list(resp.iter_lines())
    joined = "\n".join(chunks)
    assert "你好" in joined
    assert "finish_reason" in joined
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest tests/test_chat_stream.py -v`
Expected: 404 on `/api/v1/chat/stream`

- [ ] **Step 3: 实现 router.py**

Create `backend/src/chat/router.py`:

```python
import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from src.chat.llm_client import LLMClient
from src.chat.schemas import ChatRequest, ChatMessage
from src.chat.service import flatten_for_upstream
from src.config import Settings, get_settings
from src.shared.sse import sse_text_chunk, sse_done, sse_error

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(
    data: str = Form(..., description="JSON-encoded ChatRequest"),
    file: list[UploadFile] | None = File(default=None),
    settings: Settings = Depends(get_settings),
):
    try:
        req = ChatRequest(**json.loads(data))
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"invalid data: {e}")

    upstream_messages = flatten_for_upstream(req.messages)
    client = LLMClient(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        max_tokens=settings.llm_max_tokens,
        timeout=settings.llm_timeout_seconds,
    )

    async def gen() -> AsyncIterator[bytes]:
        try:
            async for piece in client.stream(upstream_messages):
                yield sse_text_chunk(piece).encode("utf-8")
            yield sse_done().encode("utf-8")
        except Exception as exc:
            logger.exception("upstream error")
            yield sse_error(str(exc)).encode("utf-8")
        finally:
            await client.aclose()

    return StreamingResponse(gen(), media_type="text/event-stream")
```

- [ ] **Step 4: 在 main.py 挂载路由**

Modify `backend/src/main.py`，在 `app.include_router(health)` 之后追加：

```python
from src.chat.router import router as chat_router
app.include_router(chat_router)
```

- [ ] **Step 5: 运行测试通过**

Run: `pytest tests/test_chat_stream.py -v`
Expected: 1 passed

- [ ] **Step 6: 真实联调上游（手动）**

Run（确认能联到 188.109.35.147 时执行）：
```bash
cd backend && source .venv/bin/activate
uvicorn src.main:app --port 8000 &
sleep 2
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -F 'data={"sessionId":"s1","messageId":"m1","messages":[{"role":"user","content":"你好"}],"think":false,"stream":true};type=application/json'
kill %1
```
Expected: 看到一连串 `data: {...}` 直到 `finish_reason: stop`。

- [ ] **Step 7: 提交**

```bash
git add backend/src/chat/router.py backend/src/main.py backend/tests/test_chat_stream.py
git commit -m "feat(backend): /api/v1/chat/stream endpoint with upstream SSE"
```

---

### Task 2.6：前端 chat.ts URL 改造 + 去掉无关 header

**Files:**
- Modify: `frontend/src/stores/modules/chat.ts`
- Modify: `frontend/src/utils/http.ts`

- [ ] **Step 1: 改 http.ts**

Replace `frontend/src/utils/http.ts` 内容为：

```ts
const BASE_URL = import.meta.env.VITE_APP_BASE_API

const httpInterceptor = {
  invoke(options: UniApp.RequestOptions) {
    options.url = !options.url.startsWith('http') ? BASE_URL + options.url : options.url
    options.timeout = 30000
    options.header = {
      ...options.header
    }
  }
}
uni.addInterceptor('request', httpInterceptor)
uni.addInterceptor('uploadFile', httpInterceptor)

interface Data<T> {
  code: number
  msg: string
  result: T
}
export function request<T>(options: UniApp.RequestOptions) {
  return new Promise<T>((resolve, reject) => {
    uni.request({
      ...options,
      success(res: UniApp.RequestSuccessCallbackResult) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
        } else {
          reject(res)
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}
```

- [ ] **Step 2: 改 chat.ts 中 5 处 URL（按精确字符串替换）**

In `frontend/src/stores/modules/chat.ts`：

替换 `/suban-h5-dx/lingxi/agent/chat/list` → `/sessions`
替换 `/suban-h5-dx/lingxi/agent/chat/${sessionId}` → `/sessions/${sessionId}/messages`
替换 `/suban-h5-dx/lingxi/agent/scene/use` → `/scene/use`
替换 `/suban-h5-dx/lingxi/agent/chat/duration/${currentMessageId.value}` → `/chat/duration/${currentMessageId.value}`
替换 fetch URL 中的 `/suban-h5-dx/lingxi/agent/v2/chat` → `/chat/stream`

（`VITE_APP_BASE_API=/api/v1` 已涵盖前缀）

同时 fetch 调用里把 `headers: { 'source-client': 'miniapp', 'Web-Authorization': 'WebBearer' }` 替换为 `headers: {}`（保留对象以便后续追加 X-Client-Id，由 Task 3.6 完成）。

- [ ] **Step 3: dev 起后端 + 前端联调**

Run（两个终端）：
```bash
# T1
cd backend && source .venv/bin/activate && uvicorn src.main:app --port 8000
# T2
cd frontend && pnpm dev
```
浏览器开 `http://localhost:8080`，发送一句"你好"，应看到流式输出。会话列表、历史等仍会 404（M3 修），不影响发对话。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/stores/modules/chat.ts frontend/src/utils/http.ts
git commit -m "feat(frontend): switch chat APIs to /api/v1/* and drop legacy headers"
git tag v0.1.0-m2
```

---

# Milestone 3：会话持久化

### Task 3.1：SQLAlchemy + database.py + 依赖注入

**Files:**
- Create: `backend/src/database.py`
- Create: `backend/tests/test_database.py`

- [ ] **Step 1: 写 failing test**

Create `backend/tests/test_database.py`:

```python
from sqlalchemy import text
from src.database import build_engine, get_sessionmaker


def test_engine_executes_wal_pragma(tmp_path):
    db_path = tmp_path / "x.sqlite"
    engine = build_engine(f"sqlite:///{db_path}")
    SessionLocal = get_sessionmaker(engine)
    with SessionLocal() as s:
        mode = s.execute(text("PRAGMA journal_mode")).scalar()
    assert str(mode).lower() == "wal"
```

- [ ] **Step 2: 运行确认失败**

Run: `pytest tests/test_database.py -v`
Expected: ImportError

- [ ] **Step 3: 实现 database.py**

Create `backend/src/database.py`:

```python
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator


class Base(DeclarativeBase):
    pass


def build_engine(db_url: str) -> Engine:
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
    )

    if db_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _pragmas(dbapi_conn, _):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA foreign_keys=ON")
            cur.execute("PRAGMA synchronous=NORMAL")
            cur.close()
    return engine


def get_sessionmaker(engine: Engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Module-level singletons wired by main.py at lifespan
_engine: Engine | None = None
_SessionLocal = None


def init_engine(db_url: str) -> None:
    global _engine, _SessionLocal
    _engine = build_engine(db_url)
    _SessionLocal = get_sessionmaker(_engine)


def get_engine() -> Engine:
    assert _engine is not None, "engine not initialized"
    return _engine


def get_db() -> Generator[Session, None, None]:
    assert _SessionLocal is not None, "sessionmaker not initialized"
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: 运行测试通过**

Run: `pytest tests/test_database.py -v`
Expected: 1 passed

- [ ] **Step 5: 提交**

```bash
git add backend/src/database.py backend/tests/test_database.py
git commit -m "feat(backend): SQLAlchemy engine with SQLite WAL pragmas"
```

---

### Task 3.2：Session/Message 模型 + 建表

**Files:**
- Create: `backend/src/sessions/__init__.py`
- Create: `backend/src/sessions/models.py`
- Modify: `backend/src/main.py`

- [ ] **Step 1: 写 models.py**

Create `backend/src/sessions/__init__.py` (空)

Create `backend/src/sessions/models.py`:

```python
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SessionRow(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), default="新对话")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )

    messages: Mapped[list["MessageRow"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="MessageRow.id",
    )

    __table_args__ = (
        Index("idx_sessions_client_updated", "client_id", "updated_at"),
    )


class MessageRow(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    message_id: Mapped[str] = mapped_column(String(64), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content_json: Mapped[str] = mapped_column(Text)
    msg_type: Mapped[str] = mapped_column(String(32), default="markdown")
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    session: Mapped[SessionRow] = relationship(back_populates="messages")
```

- [ ] **Step 2: 改 main.py，启动时建表**

Modify `backend/src/main.py` 的 `lifespan` 函数为：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    from src.database import init_engine, Base, get_engine
    from src.sessions import models as _m  # noqa: F401 import for registration
    init_engine(settings.db_url)
    Base.metadata.create_all(get_engine())
    yield
```

- [ ] **Step 3: 启动看建表**

Run:
```bash
cd backend && source .venv/bin/activate
DB_URL=sqlite:///./test.sqlite uvicorn src.main:app --port 8000 &
sleep 2
sqlite3 ./test.sqlite ".tables"
kill %1 && rm test.sqlite
```
Expected: `messages  sessions`

- [ ] **Step 4: 提交**

```bash
git add backend/src/sessions/__init__.py backend/src/sessions/models.py backend/src/main.py
git commit -m "feat(backend): Session/Message ORM models + create_all on startup"
```

---

### Task 3.3：client_id 依赖 + sessions schemas & service

**Files:**
- Create: `backend/src/shared/client_id.py`
- Create: `backend/src/sessions/schemas.py`
- Create: `backend/src/sessions/service.py`
- Create: `backend/tests/test_sessions_service.py`

- [ ] **Step 1: 写 client_id 依赖**

Create `backend/src/shared/client_id.py`:

```python
from fastapi import Header, HTTPException


def require_client_id(x_client_id: str = Header(default="")) -> str:
    if not x_client_id:
        raise HTTPException(status_code=400, detail="missing X-Client-Id header")
    return x_client_id
```

- [ ] **Step 2: 写 schemas.py**

Create `backend/src/sessions/schemas.py`:

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SessionSummary(BaseModel):
    sessionId: str
    title: str
    latestCreateTime: datetime
    model_config = ConfigDict(from_attributes=True)


class MessageOut(BaseModel):
    messageId: str
    role: str
    content: str | list[dict]
    type: str
    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel):
    code: str = "00000"
    message: str = "ok"
    data: object | None = None
```

- [ ] **Step 3: 写 service.py + failing test**

Create `backend/tests/test_sessions_service.py`:

```python
import json
import pytest
from sqlalchemy.orm import Session as OrmSession

from src.database import build_engine, get_sessionmaker, Base
from src.sessions import models  # noqa: F401
from src.sessions.service import (
    upsert_session, list_sessions, append_message, get_messages, delete_session,
)


@pytest.fixture()
def db(tmp_path) -> OrmSession:
    engine = build_engine(f"sqlite:///{tmp_path}/t.sqlite")
    Base.metadata.create_all(engine)
    SessionLocal = get_sessionmaker(engine)
    with SessionLocal() as s:
        yield s


def test_upsert_and_list(db):
    upsert_session(db, "cid", "s1", title="hello")
    upsert_session(db, "cid", "s2", title="world")
    rows = list_sessions(db, "cid")
    assert {r.id for r in rows} == {"s1", "s2"}
    rows_other = list_sessions(db, "other")
    assert rows_other == []


def test_append_and_fetch_messages(db):
    upsert_session(db, "cid", "s1")
    append_message(db, "s1", "m1", "user", "你好", "markdown")
    append_message(db, "s1", "m1", "assistant", "你好啊", "markdown")
    rows = get_messages(db, "cid", "s1")
    assert [r.role for r in rows] == ["user", "assistant"]


def test_delete_session_cascades(db):
    upsert_session(db, "cid", "s1")
    append_message(db, "s1", "m1", "user", "x", "markdown")
    delete_session(db, "cid", "s1")
    assert get_messages(db, "cid", "s1") == []
```

Run: `pytest tests/test_sessions_service.py -v`
Expected: ImportError on `src.sessions.service`

Create `backend/src/sessions/service.py`:

```python
import json
from typing import Any
from sqlalchemy import select, delete, desc
from sqlalchemy.orm import Session as OrmSession

from src.sessions.models import SessionRow, MessageRow


def upsert_session(
    db: OrmSession, client_id: str, session_id: str, *, title: str | None = None
) -> SessionRow:
    row = db.get(SessionRow, session_id)
    if row is None:
        row = SessionRow(id=session_id, client_id=client_id, title=title or "新对话")
        db.add(row)
    elif title and row.title in ("新对话", ""):
        row.title = title
    db.commit()
    db.refresh(row)
    return row


def list_sessions(db: OrmSession, client_id: str, limit: int = 50) -> list[SessionRow]:
    stmt = (
        select(SessionRow)
        .where(SessionRow.client_id == client_id)
        .order_by(desc(SessionRow.updated_at))
        .limit(limit)
    )
    return list(db.execute(stmt).scalars())


def append_message(
    db: OrmSession,
    session_id: str,
    message_id: str,
    role: str,
    content: str | list[Any],
    msg_type: str,
    duration_ms: int = 0,
) -> MessageRow:
    payload = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
    row = MessageRow(
        session_id=session_id,
        message_id=message_id,
        role=role,
        content_json=payload,
        msg_type=msg_type,
        duration_ms=duration_ms,
    )
    db.add(row)
    sess = db.get(SessionRow, session_id)
    if sess:
        from datetime import datetime, timezone
        sess.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return row


def get_messages(db: OrmSession, client_id: str, session_id: str) -> list[MessageRow]:
    sess = db.get(SessionRow, session_id)
    if sess is None or sess.client_id != client_id:
        return []
    return list(sess.messages)


def delete_session(db: OrmSession, client_id: str, session_id: str) -> bool:
    sess = db.get(SessionRow, session_id)
    if sess is None or sess.client_id != client_id:
        return False
    db.delete(sess)
    db.commit()
    return True
```

- [ ] **Step 4: 运行测试通过**

Run: `pytest tests/test_sessions_service.py -v`
Expected: 3 passed

- [ ] **Step 5: 提交**

```bash
git add backend/src/shared/client_id.py backend/src/sessions/schemas.py \
        backend/src/sessions/service.py backend/tests/test_sessions_service.py
git commit -m "feat(backend): session service layer with client_id isolation"
```

---

### Task 3.4：Sessions router

**Files:**
- Create: `backend/src/sessions/router.py`
- Modify: `backend/src/main.py`
- Create: `backend/tests/test_sessions_router.py`

- [ ] **Step 1: 写 failing test**

Create `backend/tests/test_sessions_router.py`:

```python
import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.database import init_engine, Base, get_engine
from src.sessions import models  # noqa: F401
from src.sessions.service import upsert_session, append_message
from src.database import get_sessionmaker, build_engine


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/t.sqlite"
    monkeypatch.setenv("DB_URL", db_url)
    from src.config import get_settings
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as c:
        # seed
        engine = build_engine(db_url)
        Base.metadata.create_all(engine)
        SessionLocal = get_sessionmaker(engine)
        with SessionLocal() as db:
            upsert_session(db, "cid-1", "sA", title="A")
            append_message(db, "sA", "m1", "user", "你好", "markdown")
            append_message(db, "sA", "m1", "assistant", "你好啊", "markdown")
            upsert_session(db, "cid-2", "sB", title="B")
        yield c


def test_list_sessions_filters_by_client(client):
    r = client.get("/api/v1/sessions", headers={"X-Client-Id": "cid-1"})
    assert r.status_code == 200
    data = r.json()
    assert data["code"] == "00000"
    ids = [s["sessionId"] for s in data["data"]]
    assert ids == ["sA"]


def test_get_messages(client):
    r = client.get(
        "/api/v1/sessions/sA/messages",
        headers={"X-Client-Id": "cid-1"},
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert [m["role"] for m in data] == ["user", "assistant"]


def test_other_client_cannot_read(client):
    r = client.get(
        "/api/v1/sessions/sA/messages",
        headers={"X-Client-Id": "cid-2"},
    )
    assert r.status_code == 200
    assert r.json()["data"] == []


def test_delete_session(client):
    r = client.delete(
        "/api/v1/sessions/sA",
        headers={"X-Client-Id": "cid-1"},
    )
    assert r.status_code == 200
    assert r.json()["code"] == "00000"
```

- [ ] **Step 2: 运行确认失败**

Run: `pytest tests/test_sessions_router.py -v`
Expected: 404

- [ ] **Step 3: 实现 router.py**

Create `backend/src/sessions/router.py`:

```python
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as OrmSession

from src.database import get_db
from src.sessions import service
from src.sessions.schemas import ApiResponse
from src.shared.client_id import require_client_id

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.get("")
def list_sessions(
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    rows = service.list_sessions(db, client_id)
    data = [
        {
            "sessionId": r.id,
            "title": r.title,
            "latestCreateTime": r.updated_at.isoformat(),
        }
        for r in rows
    ]
    return ApiResponse(data=data)


@router.get("/{session_id}/messages")
def get_messages(
    session_id: str,
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    rows = service.get_messages(db, client_id, session_id)
    data = []
    for r in rows:
        # content_json 可能是字符串或 JSON 数组字符串
        content: object = r.content_json
        try:
            parsed = json.loads(r.content_json)
            if isinstance(parsed, list):
                content = parsed
        except (ValueError, TypeError):
            pass
        data.append({
            "messageId": r.message_id,
            "role": r.role,
            "content": content,
            "type": r.msg_type,
        })
    return ApiResponse(data=data)


@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    ok = service.delete_session(db, client_id, session_id)
    return ApiResponse(code="00000" if ok else "10404", message="ok" if ok else "not found")
```

- [ ] **Step 4: 在 main.py 挂载路由**

Modify `backend/src/main.py`，在 chat_router 之后追加：

```python
from src.sessions.router import router as sessions_router
app.include_router(sessions_router)
```

- [ ] **Step 5: 运行测试通过**

Run: `pytest tests/test_sessions_router.py -v`
Expected: 4 passed

- [ ] **Step 6: 提交**

```bash
git add backend/src/sessions/router.py backend/src/main.py \
        backend/tests/test_sessions_router.py
git commit -m "feat(backend): sessions list/get/delete endpoints"
```

---

### Task 3.5：在 chat/stream 流程中落库 + 自动标题

**Files:**
- Modify: `backend/src/chat/router.py`
- Modify: `backend/tests/test_chat_stream.py`

- [ ] **Step 1: 增量测试**

In `backend/tests/test_chat_stream.py` 末尾追加：

```python
def test_chat_stream_persists_messages(monkeypatch, tmp_path):
    db_url = f"sqlite:///{tmp_path}/t.sqlite"
    monkeypatch.setenv("DB_URL", db_url)
    monkeypatch.setenv("LLM_BASE_URL", "http://fake-llm/v1")
    from src.config import get_settings
    get_settings.cache_clear()

    body = (
        'data: {"choices":[{"delta":{"content":"hi"}}]}\n\n'
        'data: [DONE]\n\n'
    )
    import httpx, respx, json
    from fastapi.testclient import TestClient
    from src.main import create_app
    from src.database import build_engine, get_sessionmaker, Base
    from src.sessions import models  # noqa: F401
    from src.sessions.service import get_messages, upsert_session

    with respx.mock() as r:
        r.post("http://fake-llm/v1/chat/completions").mock(
            return_value=httpx.Response(200, text=body)
        )
        with TestClient(create_app()) as client:
            payload = {
                "sessionId": "ss1",
                "messageId": "mm1",
                "messages": [{"role": "user", "content": "你好"}],
                "think": False, "stream": True,
            }
            with client.stream(
                "POST", "/api/v1/chat/stream",
                files={"data": ("data.json", json.dumps(payload), "application/json")},
                headers={"X-Client-Id": "cidX"},
            ) as resp:
                list(resp.iter_lines())

    engine = build_engine(db_url)
    SessionLocal = get_sessionmaker(engine)
    with SessionLocal() as db:
        rows = get_messages(db, "cidX", "ss1")
    roles = [r.role for r in rows]
    assert roles == ["user", "assistant"]
    assert "hi" in rows[1].content_json
```

- [ ] **Step 2: 运行确认失败**

Run: `pytest tests/test_chat_stream.py::test_chat_stream_persists_messages -v`
Expected: assertion failed（消息未落库）

- [ ] **Step 3: 改 router.py 引入落库**

Replace `backend/src/chat/router.py` 内容为：

```python
import json
import logging
import time
from typing import AsyncIterator

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as OrmSession

from src.chat.llm_client import LLMClient
from src.chat.schemas import ChatRequest
from src.chat.service import flatten_for_upstream
from src.config import Settings, get_settings
from src.database import get_db
from src.sessions import service as sess_service
from src.shared.client_id import require_client_id
from src.shared.sse import sse_text_chunk, sse_done, sse_error

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


def _derive_title(messages) -> str:
    for m in messages:
        if m.role != "user":
            continue
        if isinstance(m.content, str):
            return m.content[:30]
        for p in m.content:
            ptype = p.type if hasattr(p, "type") else p.get("type")
            if ptype == "text":
                txt = p.text if hasattr(p, "text") else p.get("text", "")
                return txt[:30]
    return "新对话"


@router.post("/stream")
async def chat_stream(
    data: str = Form(..., description="JSON-encoded ChatRequest"),
    file: list[UploadFile] | None = File(default=None),
    settings: Settings = Depends(get_settings),
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    try:
        req = ChatRequest(**json.loads(data))
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"invalid data: {e}")

    sess_service.upsert_session(db, client_id, req.sessionId, title=_derive_title(req.messages))

    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    if last_user is not None:
        sess_service.append_message(
            db, req.sessionId, req.messageId, "user",
            last_user.content, "markdown",
        )

    upstream_messages = flatten_for_upstream(req.messages)
    client = LLMClient(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        max_tokens=settings.llm_max_tokens,
        timeout=settings.llm_timeout_seconds,
    )

    async def gen() -> AsyncIterator[bytes]:
        started = time.monotonic()
        buf: list[str] = []
        try:
            async for piece in client.stream(upstream_messages):
                buf.append(piece)
                yield sse_text_chunk(piece).encode("utf-8")
            yield sse_done().encode("utf-8")
        except Exception as exc:
            logger.exception("upstream error")
            yield sse_error(str(exc)).encode("utf-8")
        finally:
            await client.aclose()
            elapsed_ms = int((time.monotonic() - started) * 1000)
            try:
                sess_service.append_message(
                    db, req.sessionId, req.messageId, "assistant",
                    "".join(buf), "markdown", duration_ms=elapsed_ms,
                )
            except Exception:
                logger.exception("persist assistant failed")

    return StreamingResponse(gen(), media_type="text/event-stream")
```

- [ ] **Step 4: 运行所有测试**

Run: `pytest -v`
Expected: 全 PASS

- [ ] **Step 5: 提交**

```bash
git add backend/src/chat/router.py backend/tests/test_chat_stream.py
git commit -m "feat(backend): persist user+assistant messages during chat stream"
```

---

### Task 3.6：前端注入 X-Client-Id

**Files:**
- Create: `frontend/src/utils/client_id.ts`
- Modify: `frontend/src/utils/http.ts`
- Modify: `frontend/src/stores/modules/chat.ts`

- [ ] **Step 1: 写 client_id.ts**

Create `frontend/src/utils/client_id.ts`:

```ts
import { v4 as uuidv4 } from 'uuid'

const KEY = 'chatbox.client_id'

export function getClientId(): string {
  try {
    const cached = localStorage.getItem(KEY)
    if (cached) return cached
    const fresh = uuidv4()
    localStorage.setItem(KEY, fresh)
    return fresh
  } catch (_e) {
    return 'anonymous'
  }
}
```

- [ ] **Step 2: 改 http.ts，在拦截器中注入头**

Modify `frontend/src/utils/http.ts` 的 `httpInterceptor.invoke` 函数为：

```ts
import { getClientId } from './client_id'

const httpInterceptor = {
  invoke(options: UniApp.RequestOptions) {
    options.url = !options.url.startsWith('http') ? BASE_URL + options.url : options.url
    options.timeout = 30000
    options.header = {
      ...options.header,
      'X-Client-Id': getClientId()
    }
  }
}
```

- [ ] **Step 3: 改 chat.ts 中 fetch（SSE 通道）也加上头**

In `frontend/src/stores/modules/chat.ts`：找到 `fetch(...)` 调用里的 `headers: {}` 替换为：

```ts
import { getClientId } from '@/utils/client_id'

// ...
headers: {
  'X-Client-Id': getClientId()
}
```

确保 `import` 在文件顶端只加一次。

- [ ] **Step 4: 浏览器联调**

刷新前端，发对话；F12 Network 看到所有请求都带 `X-Client-Id`；侧边栏会话列表能从 SQLite 中加载；清 localStorage 后再发对话，旧会话消失（隔离生效）。

- [ ] **Step 5: 提交并打 tag**

```bash
git add frontend/src/utils/client_id.ts frontend/src/utils/http.ts \
        frontend/src/stores/modules/chat.ts
git commit -m "feat(frontend): generate and send X-Client-Id for session isolation"
git tag v0.1.0-m3
```

---

# Milestone 4：文件上传 + 多模态结构

### Task 4.1：File 模型 + 抽取器（pdf/docx/txt）

**Files:**
- Create: `backend/src/files/__init__.py`
- Create: `backend/src/files/models.py`
- Create: `backend/src/files/extractor.py`
- Create: `backend/tests/test_extractor.py`

- [ ] **Step 1: 写 models.py**

Create `backend/src/files/__init__.py` (空)

Create `backend/src/files/models.py`:

```python
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FileRow(Base):
    __tablename__ = "files"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # uuid
    client_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[str | None] = mapped_column(
        ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True
    )
    message_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(512))
    mime: Mapped[str] = mapped_column(String(128), default="application/octet-stream")
    size: Mapped[int] = mapped_column(Integer, default=0)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
```

并在 `backend/src/main.py` 的 lifespan 中追加 `from src.files import models as _fm  # noqa: F401`。

- [ ] **Step 2: 写 extractor 测试**

Create `backend/tests/test_extractor.py`:

```python
import io
from src.files.extractor import extract_text


def test_extract_txt(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hello 中文", encoding="utf-8")
    text = extract_text(str(p), "text/plain", "a.txt")
    assert "hello" in text
    assert "中文" in text


def test_extract_unsupported_returns_empty(tmp_path):
    p = tmp_path / "a.bin"
    p.write_bytes(b"\x00\x01\x02")
    text = extract_text(str(p), "application/octet-stream", "a.bin")
    assert text == ""
```

- [ ] **Step 3: 运行确认失败**

Run: `pytest tests/test_extractor.py -v`
Expected: ImportError

- [ ] **Step 4: 实现 extractor.py**

Create `backend/src/files/extractor.py`:

```python
import logging
import os

logger = logging.getLogger(__name__)


def _ext(name: str) -> str:
    return os.path.splitext(name)[1].lower()


def extract_text(path: str, mime: str, original_name: str) -> str:
    ext = _ext(original_name)
    try:
        if ext in (".txt", ".md", ".csv", ".log") or mime.startswith("text/"):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        if ext == ".pdf" or mime == "application/pdf":
            return _extract_pdf(path)
        if ext == ".docx":
            return _extract_docx(path)
    except Exception:
        logger.exception("extract failed for %s", original_name)
    return ""


def _extract_pdf(path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(path)
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _extract_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)
```

- [ ] **Step 5: 运行测试通过**

Run: `pytest tests/test_extractor.py -v`
Expected: 2 passed

- [ ] **Step 6: 提交**

```bash
git add backend/src/files/__init__.py backend/src/files/models.py \
        backend/src/files/extractor.py backend/src/main.py \
        backend/tests/test_extractor.py
git commit -m "feat(backend): File model + pdf/docx/txt text extractor"
```

---

### Task 4.2：File service + 静态下载 + 上传接口

**Files:**
- Create: `backend/src/files/schemas.py`
- Create: `backend/src/files/service.py`
- Create: `backend/src/files/router.py`
- Modify: `backend/src/main.py`

- [ ] **Step 1: 写 schemas.py**

Create `backend/src/files/schemas.py`:

```python
from pydantic import BaseModel


class FileMeta(BaseModel):
    file_id: str
    name: str
    url: str
    mime: str
    size: int
```

- [ ] **Step 2: 写 service.py**

Create `backend/src/files/service.py`:

```python
import os
import uuid
from sqlalchemy.orm import Session as OrmSession

from src.config import get_settings
from src.files.extractor import extract_text
from src.files.models import FileRow


async def save_upload(db: OrmSession, *, client_id: str, session_id: str | None,
                      filename: str, content: bytes, mime: str) -> FileRow:
    settings = get_settings()
    file_id = uuid.uuid4().hex
    subdir = session_id or "_loose"
    base_dir = os.path.abspath(settings.upload_dir)
    target_dir = os.path.join(base_dir, subdir)
    os.makedirs(target_dir, exist_ok=True)
    safe_name = filename.replace("/", "_").replace("\\", "_")
    stored = os.path.join(target_dir, f"{file_id}_{safe_name}")
    with open(stored, "wb") as f:
        f.write(content)
    text = extract_text(stored, mime, safe_name)
    row = FileRow(
        id=file_id, client_id=client_id, session_id=session_id,
        original_name=safe_name, stored_path=stored, mime=mime, size=len(content),
        extracted_text=text,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_file(db: OrmSession, client_id: str, file_id: str) -> FileRow | None:
    row = db.get(FileRow, file_id)
    if row is None or row.client_id != client_id:
        return None
    return row


def texts_for(db: OrmSession, file_ids: list[str]) -> dict[str, str]:
    if not file_ids:
        return {}
    rows = db.query(FileRow).filter(FileRow.id.in_(file_ids)).all()
    return {r.id: r.extracted_text or "" for r in rows}
```

- [ ] **Step 3: 写 router.py**

Create `backend/src/files/router.py`:

```python
import os
import mimetypes
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session as OrmSession

from src.database import get_db
from src.files import service
from src.shared.client_id import require_client_id

router = APIRouter(prefix="/api/v1/files", tags=["files"])


@router.post("")
async def upload(
    file: UploadFile = File(...),
    sessionId: str | None = None,
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    content = await file.read()
    mime = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
    row = await service.save_upload(
        db, client_id=client_id, session_id=sessionId,
        filename=file.filename or "file.bin",
        content=content, mime=mime,
    )
    return {
        "code": "00000",
        "data": {
            "file_id": row.id,
            "name": row.original_name,
            "url": f"/files/{row.id}",
            "mime": row.mime, "size": row.size,
        },
    }


download_router = APIRouter(tags=["files"])


@download_router.get("/files/{file_id}")
def download(
    file_id: str,
    client_id: str = Depends(require_client_id),
    db: OrmSession = Depends(get_db),
):
    row = service.get_file(db, client_id, file_id)
    if row is None or not os.path.exists(row.stored_path):
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(row.stored_path, media_type=row.mime, filename=row.original_name)
```

- [ ] **Step 4: 挂到 main.py**

Modify `backend/src/main.py`，在挂载其它路由后追加：

```python
from src.files.router import router as files_router, download_router
app.include_router(files_router)
app.include_router(download_router)
```

- [ ] **Step 5: 简单冒烟（手动）**

Run:
```bash
cd backend && source .venv/bin/activate
DB_URL=sqlite:///./scratch.sqlite UPLOAD_DIR=./_up uvicorn src.main:app --port 8000 &
sleep 2
echo "hello chatbox" > /tmp/_a.txt
curl -s -X POST http://localhost:8000/api/v1/files \
  -H 'X-Client-Id: t' -F 'file=@/tmp/_a.txt'
kill %1
rm -rf scratch.sqlite _up /tmp/_a.txt
```
Expected: 返回 `{code:"00000", data:{file_id, name:"_a.txt", url:"/files/<id>", ...}}`

- [ ] **Step 6: 提交**

```bash
git add backend/src/files/schemas.py backend/src/files/service.py \
        backend/src/files/router.py backend/src/main.py
git commit -m "feat(backend): file upload + download endpoints"
```

---

### Task 4.3：chat/stream 携带 file_ids → 抽取文本拼到 prompt

**Files:**
- Modify: `backend/src/chat/router.py`
- Modify: `backend/tests/test_chat_stream.py`

- [ ] **Step 1: 增量测试**

In `backend/tests/test_chat_stream.py` 末尾追加：

```python
def test_chat_stream_injects_file_text(monkeypatch, tmp_path):
    db_url = f"sqlite:///{tmp_path}/t.sqlite"
    monkeypatch.setenv("DB_URL", db_url)
    monkeypatch.setenv("LLM_BASE_URL", "http://fake-llm/v1")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "up"))
    from src.config import get_settings
    get_settings.cache_clear()

    import httpx, respx, json
    from fastapi.testclient import TestClient
    from src.main import create_app

    captured_body = {}

    def _capture(request: httpx.Request):
        captured_body["payload"] = json.loads(request.content)
        body = 'data: {"choices":[{"delta":{"content":"ok"}}]}\n\ndata: [DONE]\n\n'
        return httpx.Response(200, text=body)

    with respx.mock() as r:
        r.post("http://fake-llm/v1/chat/completions").mock(side_effect=_capture)
        with TestClient(create_app()) as client:
            # 先上传一个文件
            up = client.post(
                "/api/v1/files",
                headers={"X-Client-Id": "cidF"},
                files={"file": ("note.txt", "重要语料 abc", "text/plain")},
            )
            file_id = up.json()["data"]["file_id"]
            # 发起会话，附带 file_id
            payload = {
                "sessionId": "ssf", "messageId": "mmf",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请总结附件"},
                        {"type": "file", "file": {"file_id": file_id, "name": "note.txt", "url": f"/files/{file_id}"}},
                    ],
                }],
                "file_ids": [file_id],
                "think": False, "stream": True,
            }
            with client.stream(
                "POST", "/api/v1/chat/stream",
                files={"data": ("data.json", json.dumps(payload), "application/json")},
                headers={"X-Client-Id": "cidF"},
            ) as resp:
                list(resp.iter_lines())

    upstream_content = captured_body["payload"]["messages"][0]["content"]
    assert "重要语料 abc" in upstream_content
    assert "note.txt" in upstream_content
```

- [ ] **Step 2: 运行确认失败**

Run: `pytest tests/test_chat_stream.py::test_chat_stream_injects_file_text -v`
Expected: 失败（当前 flatten 没拿到 file_texts）

- [ ] **Step 3: 改 router 把 file_ids 抽出的文本传入 flatten**

In `backend/src/chat/router.py` 的 `chat_stream` 函数中，把 `upstream_messages = flatten_for_upstream(req.messages)` 替换为：

```python
from src.files import service as files_service
file_texts = files_service.texts_for(db, req.file_ids)
upstream_messages = flatten_for_upstream(req.messages, file_texts=file_texts)
```

- [ ] **Step 4: 运行测试通过**

Run: `pytest -v`
Expected: 全 PASS

- [ ] **Step 5: 提交**

```bash
git add backend/src/chat/router.py backend/tests/test_chat_stream.py
git commit -m "feat(backend): inject extracted file text into upstream prompt"
```

---

### Task 4.4：前端发送侧改造（FormData 带文件 + content 多模态）

**Files:**
- Modify: `frontend/src/stores/modules/chat.ts`

- [ ] **Step 1: 修改 sendQuestion，构造多模态 content + file_ids**

In `frontend/src/stores/modules/chat.ts` 的 `sendQuestion` 函数中：

1. **上传文件**：在 `if (files && files.length > 0)` 块**之前**先把文件逐个 POST 到 `/files`，收集 `fileMetaList: {file_id, name, url, mime, size}[]`。
2. **构造 messages 时**：若 `fileMetaList.length > 0`，把当前 prompt 转为 content 数组：
   ```ts
   const parts: any[] = [{ type: 'text', text: prompt }]
   fileMetaList.forEach(fm => parts.push({ type: 'file', file: { file_id: fm.file_id, name: fm.name, url: fm.url } }))
   ```
3. **chatRequest 增加 `file_ids: fileMetaList.map(f => f.file_id)`**。

完整改造段（替换 sendQuestion 内部从 `try {` 到对应 `fetch(...)` 调用之前的相关逻辑），最小化补丁如下：

在原 `// 启动轮询` 之后插入：

```ts
const baseApi = import.meta.env.VITE_APP_BASE_API as string
const fileMetaList: { file_id: string; name: string; url: string; mime: string; size: number }[] = []
if (files && files.length > 0) {
  for (const f of files) {
    const fd = new FormData()
    fd.append('file', f)
    const r = await fetch(`${baseApi}/files?sessionId=${encodeURIComponent(sessionStore.currentSessionId)}`, {
      method: 'POST',
      headers: { 'X-Client-Id': getClientId() },
      body: fd
    })
    const j = await r.json()
    if (j.code === '00000') fileMetaList.push(j.data)
  }
}
```

在构建 `messages` 数组的 `.map(m => ({...}))` 之后，如果 `fileMetaList.length > 0`，把最后一条 user 消息的 content 替换为多模态数组：

```ts
if (fileMetaList.length > 0) {
  const lastUser = [...messages].reverse().find(m => m.role === 'user')
  if (lastUser) {
    const parts: any[] = [{ type: 'text', text: typeof lastUser.content === 'string' ? lastUser.content : String(lastUser.content) }]
    fileMetaList.forEach(fm => parts.push({ type: 'file', file: { file_id: fm.file_id, name: fm.name, url: fm.url } }))
    lastUser.content = parts as any
  }
}
```

在 `chatRequest` 对象上追加：

```ts
chatRequest.file_ids = fileMetaList.map(f => f.file_id)
```

并在原本 `if (files && files.length > 0) { files.forEach(...) formData.append('file', file) }` 这一段把文件直接附到 `formData` 的逻辑**删除**（避免重复传文件；文件已通过 `/files` 上传）。`formData` 只保留 `data` 字段。

- [ ] **Step 2: 渲染侧（message_item.vue 兼容多模态 content）**

Modify `frontend/src/pages/network-agent/components/Message/message_item.vue`：

在模板里渲染气泡 content 之前增加一个 computed，把数组 content 拼成 markdown：

```vue
<script setup lang="ts">
// 已有 props.item
import { computed } from 'vue'
const renderedContent = computed(() => {
  const c: any = (props as any).item?.content
  if (typeof c === 'string') return c
  if (Array.isArray(c)) {
    return c.map((p: any) => {
      if (p.type === 'text') return p.text
      if (p.type === 'file') return `📎 [${p.file?.name}](${p.file?.url})`
      if (p.type === 'image_url') return `![image](${p.image_url?.url})`
      return ''
    }).join('\n')
  }
  return ''
})
</script>
```

把模板里所有原本读 `item.content` 用于 markdown 渲染的位置改读 `renderedContent`（保留 type/answerType 等字段判定不变）。

- [ ] **Step 3: 浏览器联调**

刷新前端，选一个 `.txt` 或 `.pdf` 上传 + 发问"总结这份文档"。Network 面板：
1. 看到 `POST /api/v1/files` 200。
2. 看到 `POST /api/v1/chat/stream` 的 multipart 中 `data.file_ids` 包含 file_id。
3. 模型回复中能引用文件内容。

- [ ] **Step 4: 提交**

```bash
git add frontend/src/stores/modules/chat.ts \
        frontend/src/pages/network-agent/components/Message/message_item.vue
git commit -m "feat(frontend): upload files separately and send multimodal content parts"
git tag v0.1.0-m4
```

---

# Milestone 5：兼容端点 + 错误处理 + 日志 + 文档 + 离线包

### Task 5.1：兼容 scene/use + chat/duration 占位

**Files:**
- Create: `backend/src/compat/__init__.py`
- Create: `backend/src/compat/router.py`
- Modify: `backend/src/main.py`

- [ ] **Step 1: 写 router.py**

Create `backend/src/compat/__init__.py` (空)

Create `backend/src/compat/router.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy import select

from src.database import get_db
from src.sessions.models import MessageRow

router = APIRouter(prefix="/api/v1", tags=["compat"])


@router.post("/scene/use")
async def scene_use() -> dict:
    return {"code": "00000", "data": []}


@router.get("/chat/duration/{message_id}")
async def chat_duration(message_id: str, db: OrmSession = Depends(get_db)) -> dict:
    stmt = (
        select(MessageRow.duration_ms)
        .where(MessageRow.message_id == message_id, MessageRow.role == "assistant")
        .order_by(MessageRow.id.desc())
        .limit(1)
    )
    val = db.execute(stmt).scalar()
    return {"code": "00000", "data": int(val) if val else 0}
```

- [ ] **Step 2: 挂到 main.py**

Modify `backend/src/main.py`：

```python
from src.compat.router import router as compat_router
app.include_router(compat_router)
```

- [ ] **Step 3: 提交**

```bash
git add backend/src/compat/ backend/src/main.py
git commit -m "feat(backend): compat endpoints for scene/use and chat/duration"
```

---

### Task 5.2：全局错误处理

**Files:**
- Create: `backend/src/shared/exceptions.py`
- Modify: `backend/src/main.py`

- [ ] **Step 1: 写 exceptions.py**

Create `backend/src/shared/exceptions.py`:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    def __init__(self, status_code: int, error_code: str, detail: str):
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail


def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def _app_exc(_req: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.error_code, "message": exc.detail, "data": None},
        )

    @app.exception_handler(RequestValidationError)
    async def _val_exc(_req: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"code": "VALIDATION_ERROR", "message": str(exc.errors()), "data": None},
        )
```

- [ ] **Step 2: 在 main.py 注册**

Modify `backend/src/main.py`，在 `create_app` 中 `app.add_middleware(CORS...)` 之后追加：

```python
from src.shared.exceptions import register_handlers
register_handlers(app)
```

- [ ] **Step 3: 提交**

```bash
git add backend/src/shared/exceptions.py backend/src/main.py
git commit -m "feat(backend): unified exception handlers"
```

---

### Task 5.3：文档：architecture.md

**Files:**
- Create: `docs/architecture.md`

- [ ] **Step 1: 写架构文档**

Create `chatbox-private/docs/architecture.md`:

````markdown
# 架构说明

## 组件拓扑

```
Browser
  │  HTTP (80/8080)
  ▼
[Web 容器: nginx]
  ├── /                  → 静态 H5（uni-app build:h5 产物）
  ├── /api/*             → proxy → api:8000
  └── /files/*           → proxy → api:8000
              │
              ▼
        [API 容器: FastAPI + Uvicorn]
              │  httpx async, stream
              ▼
        [Upstream LLM @ 188.109.35.147:9092]
              │
   持久化：
  ┌── SQLite (./data/db/chatbox.sqlite, WAL)
  └── Upload files (./data/uploads/<session>/<uuid>_<name>)
```

## 关键数据流：对话 SSE

1. 前端 `chat.ts` 把会话历史拼到 `messages[]`，POST `multipart/form-data` 到 `/api/v1/chat/stream`，header 带 `X-Client-Id`。
2. 后端解析 `data` JSON 字段 → ChatRequest；落库 user 消息；按 `file_ids` 拉取已上传文件的抽取文本。
3. `flatten_for_upstream` 把多模态 parts 数组扁平化成上游兼容的纯文本 content。
4. `LLMClient.stream` 调用上游 `/v1/chat/completions` (stream=true)。
5. 每个 delta.content → 编码为 `data: {code, choices:[{type, message:{content}}]}\n\n` 下发。
6. 结束帧 `finish_reason=stop` + 落库 assistant 全文 + 写入 duration。

## 会话隔离

- 浏览器首次加载 `client_id.ts` 生成 UUID → localStorage。
- 所有请求 header 注入 `X-Client-Id`。
- 后端 `sessions.client_id` 列过滤；删除/查询都以此为权限边界。

## 文件多模态

- 数据库 `messages.content_json` 存 OpenAI parts 数组的 JSON。
- `files.extracted_text` 缓存抽取文本，避免重复解析。
- 当前模型非多模态：转发前由 `flatten_for_upstream` 降级为纯文本。
- 未来切多模态：改 `flatten_for_upstream` 透传数组即可，存储层不变。

## 目录映射

| 容器路径 | 宿主路径 | 用途 |
|---|---|---|
| /data/db | ./data/db | SQLite 文件 |
| /data/uploads | ./data/uploads | 用户上传 |
````

- [ ] **Step 2: 提交**

```bash
git add docs/architecture.md
git commit -m "docs: architecture overview"
```

---

### Task 5.4：文档：deployment.md（含离线镜像）

**Files:**
- Create: `docs/deployment.md`
- Create: `scripts/offline-bundle.sh`

- [ ] **Step 1: 写部署文档**

Create `chatbox-private/docs/deployment.md`:

````markdown
# 部署手册

## 1. 联网环境部署

```bash
cp .env.example .env
# 编辑 .env：必填 LLM_BASE_URL 与 LLM_MODEL
docker compose up -d --build
docker compose ps
curl http://localhost:${WEB_PORT:-8080}/api/v1/health
```

健康响应 `{"status":"ok"}` 即成功。

## 2. 离线（私域无外网）部署

### 2.1 在联网机器上打包镜像

```bash
./scripts/offline-bundle.sh
# 产出 ./chatbox-bundle.tar.gz（含 web + api 镜像 + compose + docs + scripts）
```

### 2.2 上传到目标机器

```bash
scp chatbox-bundle.tar.gz user@target:/opt/
ssh user@target
cd /opt && tar -xzf chatbox-bundle.tar.gz && cd chatbox-bundle
```

### 2.3 加载镜像并启动

```bash
docker load -i images/chatbox-web.tar
docker load -i images/chatbox-api.tar
cp .env.example .env  # 按现场修改
docker compose -f docker-compose.yml up -d
```

## 3. 日常运维

| 操作 | 命令 |
|---|---|
| 查看日志 | `docker compose logs -f api` / `... web` |
| 重启 | `docker compose restart api` |
| 拉起最新代码 | `git pull && docker compose up -d --build` |
| 备份数据 | `tar -czf backup-$(date +%F).tgz data/` |
| 恢复 | 停服 → 解压覆盖 `data/` → 启服 |

## 4. 升级回滚

构建镜像时本地打 tag：`docker tag chatbox-api:latest chatbox-api:v0.1.x`。
回滚：修改 `docker-compose.yml` 中 image 字段为旧 tag，重启。

## 5. 常见故障

| 现象 | 排查 |
|---|---|
| 前端打开白屏 | `docker compose logs web`；确认 nginx.conf 已构建进镜像 |
| `/api/v1/health` 502 | api 容器未健康；`docker compose logs api` |
| 对话无响应 | 检查 LLM_BASE_URL 可达；`docker compose exec api curl $LLM_BASE_URL/models` |
| 上传超时 | 调大 nginx `client_max_body_size` 与 `proxy_read_timeout` |
````

- [ ] **Step 2: 写打包脚本**

Create `chatbox-private/scripts/offline-bundle.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/.bundle"
OUT="$ROOT/chatbox-bundle.tar.gz"

rm -rf "$WORK" && mkdir -p "$WORK/images"

cd "$ROOT"
docker compose build
docker save -o "$WORK/images/chatbox-web.tar" "$(docker compose images web -q)"
docker save -o "$WORK/images/chatbox-api.tar" "$(docker compose images api -q)"

cp docker-compose.yml "$WORK/"
cp .env.example "$WORK/"
cp -R docs "$WORK/docs"
cp -R scripts "$WORK/scripts"
cp README.md "$WORK/" || true

tar -czf "$OUT" -C "$ROOT" .bundle
mv "$WORK"/* "$ROOT/.bundle_flat/" 2>/dev/null || true
rm -rf "$WORK"
echo "Bundle written: $OUT"
```

Run:
```bash
chmod +x scripts/offline-bundle.sh
```

- [ ] **Step 3: 提交**

```bash
git add docs/deployment.md scripts/offline-bundle.sh
git commit -m "docs: deployment guide + offline bundle script"
```

---

### Task 5.5：文档：usage.md + api.md

**Files:**
- Create: `docs/usage.md`
- Create: `docs/api.md`

- [ ] **Step 1: 写 usage.md**

Create `chatbox-private/docs/usage.md`:

````markdown
# 使用指南

## 终端用户

- 浏览器访问 `http://<部署机器>:<WEB_PORT>`。
- 首次打开自动分配匿名身份；同一浏览器复用历史，清浏览器数据即新身份。
- 输入框右侧的回形针按钮可上传 `.txt/.md/.pdf/.docx`，模型会读取其内容回答。
- 历史会话在左侧栏，点击可回放；删除按钮可移除会话。

## 二次开发

### 本地启动（不依赖 Docker）

```bash
# 后端
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload --port 8000

# 前端
cd ../frontend
pnpm install
pnpm dev   # 8080，自动代理 /api → localhost:8000
```

### 切换上游模型

编辑 `.env` 中 `LLM_BASE_URL`、`LLM_MODEL`，重启 api 容器即可。任何 OpenAI 兼容 `/v1/chat/completions` 端点都能接入。

### 接入需要鉴权的网关

填 `LLM_API_KEY=...`，会自动以 `Authorization: Bearer ...` 注入。

### 添加新业务路由

在 `backend/src/<domain>/` 下新建 `router.py / schemas.py / service.py / models.py`，在 `main.py` 中 `include_router`。遵循 `cxy-suban-lingxi/docs/reference/fastapi-best-practices.md`。

### 单元测试

```bash
cd backend && pytest -v
```
````

- [ ] **Step 2: 写 api.md**

Create `chatbox-private/docs/api.md`:

````markdown
# 后端 API 契约 (v1)

所有请求必须携带 `X-Client-Id` 头（无鉴权场景下作为身份标识）。成功响应统一形如 `{code: "00000", message, data}`。

## 健康检查

`GET /api/v1/health` → `{status: "ok"}`

## 会话

### 列表
`GET /api/v1/sessions`
```json
{"code":"00000","data":[{"sessionId":"...","title":"...","latestCreateTime":"..."}]}
```

### 历史消息
`GET /api/v1/sessions/{session_id}/messages`
```json
{"code":"00000","data":[{"messageId":"...","role":"user","content":"...","type":"markdown"}]}
```
注：`content` 可能是字符串或多模态 parts 数组。

### 删除
`DELETE /api/v1/sessions/{session_id}` → `{code:"00000"}`

## 对话流

`POST /api/v1/chat/stream`，`multipart/form-data`：
- `data`：JSON 字符串
  ```json
  {
    "sessionId": "uuid",
    "messageId": "uuid",
    "messages": [
      {"role":"user","content":"你好"},
      {"role":"user","content":[
        {"type":"text","text":"总结这份文档"},
        {"type":"file","file":{"file_id":"...","name":"a.pdf","url":"/files/..."}}
      ]}
    ],
    "file_ids": ["..."],
    "think": false,
    "stream": true
  }
  ```
- `file`（可选，已废弃，请走 `/api/v1/files`）

返回 `text/event-stream`，帧格式：
```
data: {"code":"00000","choices":[{"type":"markdown","message":{"content":"片段"}}]}

data: {"code":"00000","choices":[{"finish_reason":"stop"}]}
```

## 文件

### 上传
`POST /api/v1/files?sessionId=<可选>`，form `file=<binary>`
```json
{"code":"00000","data":{"file_id":"...","name":"a.pdf","url":"/files/...","mime":"...","size":1234}}
```

### 下载
`GET /files/{file_id}`，header 需带 `X-Client-Id`（仅 owner 可下载）。

## 兼容（前端遗留）

- `POST /api/v1/scene/use` → 空 `data: []`
- `GET /api/v1/chat/duration/{messageId}` → `{data: <毫秒数>}`
````

- [ ] **Step 3: 提交**

```bash
git add docs/usage.md docs/api.md
git commit -m "docs: usage and api reference"
```

---

### Task 5.6：端到端冒烟验证 + tag

**Files:**（无新增）

- [ ] **Step 1: 全部测试**

```bash
cd backend && source .venv/bin/activate && pytest -v
```
Expected: 所有测试 PASS。

- [ ] **Step 2: docker compose 全链路**

```bash
cd /Users/jia/MyProjects/pythonProjects/cmcc_cxy/Bprocss/chatbox-private
docker compose down -v
docker compose up -d --build
sleep 6
curl -s http://localhost:8080/api/v1/health
```
Expected: `{"status":"ok"}`

浏览器：
1. 打开 `http://localhost:8080`。
2. 发送一句"你好"，观察流式输出正常。
3. 上传一个小 `.txt`，问"总结附件"。
4. 刷新页面，左侧历史能看到刚才的会话。
5. 打开匿名窗口（清缓存），看不到上一身份的会话。

- [ ] **Step 3: 打包离线 bundle**

```bash
./scripts/offline-bundle.sh
ls -lh chatbox-bundle.tar.gz
```
Expected: 文件存在。

- [ ] **Step 4: 收尾提交并打 tag**

```bash
docker compose down
git add -A
git commit -m "chore: m5 verification + bundle" --allow-empty
git tag v0.1.0-m5
git tag v0.1.0
```

---

## 自检（写完计划后，与方案核对）

**1. 需求覆盖：**
- 独立 git 仓库 → Task 1.1 ✓
- 仅 H5 部署 → Task 1.4/1.5 ✓
- OpenAI 兼容 SSE → Task 2.2 + 2.5 ✓
- 会话历史 → Task 3.2–3.5 ✓
- client_id 隔离 → Task 3.3/3.6 ✓
- 文件上传 + 多模态结构兼容 → Task 4.1–4.4 ✓
- 文档（架构/部署/使用/API）→ Task 5.3–5.5 ✓
- Docker 一键 → Task 1.5/1.6/1.7 ✓
- 离线镜像 → Task 5.4 ✓
- 遵循 docs/reference 规范 → 每个 backend 任务用 APIRouter、依赖注入、pydantic schema、SQLAlchemy 2.x + WAL，参考 fastapi/sqlite/deployment 三份最佳实践 ✓

**2. 类型一致性：**
- `ChatRequest` 字段：sessionId/messageId/messages/think/stream/file_ids → router/service/前端 chat.ts 一致。
- `sessions.client_id` 列贯穿 service/router/前端 header。
- SSE 帧字段 `code/choices[].type/message.content/finish_reason` 与前端 `processStreamChunk` 解析逻辑（在 lingxi 原 chat.ts，沿用）一致。

**3. 占位扫描：** 无 TBD / "稍后" / "添加错误处理" 等空泛词。

---

## 执行方式选择

**Plan complete and saved to `chatbox-private/PLAN.md`. Two execution options:**

**1. Subagent-Driven（推荐）** — 我为每个任务派发独立 subagent，任务间复核，迭代快。

**2. Inline Execution** — 在当前会话中按 executing-plans 批量执行，到 checkpoint 暂停复核。

**选哪个？**
