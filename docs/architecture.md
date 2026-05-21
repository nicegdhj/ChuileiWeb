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
        [Upstream LLM]
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
- 当前 flatten 把 `file` 类型 parts 拼成纯文本追加到 prompt；如未来模型支持多模态，仅需改 `flatten_for_upstream`。
