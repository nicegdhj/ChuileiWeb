# chatbox-private

私域内网部署的对话式 AI 应用，前端从 lingxi 迁移并精简为 H5；后端为 FastAPI 适配层，接入 OpenAI 兼容的私有大模型。

## 前置条件

- Docker >= 24.0
- Docker Compose >= 2.0（通常随 Docker Desktop 一并安装）

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
- `docs/`：架构 / 部署 / 使用 / API 文档
- `data/`：运行时数据卷（SQLite 与上传文件）

## 文档

- 架构：[docs/architecture.md](docs/architecture.md)
- 部署：[docs/deployment.md](docs/deployment.md)
- 使用：[docs/usage.md](docs/usage.md)
- API：[docs/api.md](docs/api.md)
