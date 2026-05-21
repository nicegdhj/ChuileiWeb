# API 契约

所有端点前缀 `/api/v1`，内容类型默认 `application/json`，需在 Header 携带 `X-Client-Id: <uuid>`。

## POST /api/v1/chat/stream

流式对话。请求体为 `multipart/form-data`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | File（JSON） | 序列化为 JSON 的 `ChatRequest` |

### ChatRequest 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `sessionId` | string | 会话 ID |
| `messageId` | string | 本次消息 ID |
| `messages` | array | 对话历史，OpenAI messages 格式 |
| `think` | bool | 是否开启深度思考 |
| `stream` | bool | 必须为 true |
| `file_ids` | string[] | 已上传文件 ID 列表（可选） |

### SSE 帧格式

```
data: {"code":"00000","choices":[{"type":"markdown","message":{"content":"..."}}]}\n\n
data: {"code":"00000","choices":[{"finish_reason":"stop"}]}\n\n
```

---

## GET /api/v1/sessions

返回当前 client_id 的会话列表（最多 50 条，按更新时间倒序）。

**Response:**
```json
{ "code": "00000", "data": [{ "sessionId": "...", "title": "...", "latestCreateTime": "..." }] }
```

---

## GET /api/v1/sessions/{session_id}/messages

返回指定会话的消息列表。

---

## DELETE /api/v1/sessions/{session_id}

删除指定会话及其所有消息。

---

## POST /api/v1/files

上传文件。请求体为 `multipart/form-data`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | File | 文件内容 |
| `sessionId` | string（query） | 关联会话（可选） |

**Response:**
```json
{ "code": "00000", "data": { "file_id": "...", "name": "...", "url": "/files/...", "mime": "...", "size": 1024 } }
```

---

## GET /files/{file_id}

下载文件（需 `X-Client-Id` 匹配上传者）。

---

## POST /api/v1/scene/use

兼容端点，返回空列表。

## GET /api/v1/chat/duration/{message_id}

返回指定消息的 LLM 响应耗时（毫秒）。

## GET /api/v1/health

健康检查，返回 `{"status":"ok"}`。
