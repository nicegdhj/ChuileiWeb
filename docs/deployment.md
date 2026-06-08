# 部署手册

## 前置条件

- Docker >= 24
- Docker Compose plugin (`docker compose` v2)
- 内网可达上游 LLM 端点

## 快速启动

```bash
cp .env.example .env
# 编辑 .env，设置 LLM_BASE_URL / LLM_MODEL / LLM_API_KEY / WEB_PORT
docker compose up -d --build
```

访问：`http://<host>:<WEB_PORT>`

## 环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LLM_BASE_URL` | — | 上游 LLM base URL，如 `http://host:9092/v1` |
| `LLM_MODEL` | `qwen3-32b` | 模型 ID |
| `LLM_API_KEY` | 空 | 若上游需要鉴权则填写 |
| `LLM_MAX_TOKENS` | `32000` | 最大 token 数 |
| `LLM_TIMEOUT_SECONDS` | `120` | 上游超时（秒） |
| `WEB_PORT` | `8088` | Host 暴露端口 |
| `DB_URL` | `sqlite:///./data/db/chatbox.sqlite` | SQLite 路径 |
| `UPLOAD_DIR` | `./data/uploads` | 文件上传目录 |

## 数据持久化

```yaml
volumes:
  - ./data/db:/data/db
  - ./data/uploads:/data/uploads
```

数据卷挂载到宿主机 `./data/`，重建容器不丢失。

## 离线部署（内网无外网）

```bash
# 在有网机器上打包
bash scripts/offline-bundle.sh

# 在目标机器上加载
docker load -i chatbox-private-images.tar
docker compose up -d
```

## 升级

```bash
docker compose pull   # 如有公开镜像
docker compose up -d --build
```

## 日志

```bash
docker compose logs -f api
docker compose logs -f web
```
