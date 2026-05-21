# 使用指南

## 用户操作

### 基本对话

1. 打开 `http://<host>:<WEB_PORT>` 。
2. 在底部输入框输入问题，点击发送或按 Enter。
3. 助手以流式方式逐字返回回答。

### 深度思考模式

点击输入框旁的「深度思考」按钮开启，模型会输出推理链（`<think>` 标签内容折叠展示）。

### 上传文件

点击回形针图标选择文件（支持 `.txt` / `.md` / `.pdf` / `.docx`），文件内容会自动抽取并拼入 prompt。

### 会话管理

- 左侧侧边栏显示历史会话，点击切换。
- 点击「新对话」开始新的会话。
- 点击会话右侧删除按钮可删除该会话。

### 隐私隔离

每个浏览器实例生成唯一 `client_id`（存于 localStorage），清除 localStorage 后历史会话不再可见（数据仍在服务器，但无法关联回该客户端）。

## 开发者指南

### 本地开发（仅 backend）

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
LLM_BASE_URL=http://... uvicorn src.main:app --reload --port 8000
```

### 本地开发（仅 frontend）

```bash
cd frontend
pnpm install
# 设置 .env.development 中 VITE_APP_BASE_API=http://localhost:8000/api/v1
pnpm dev:h5
```

### 运行测试

```bash
cd backend
python -m pytest -v
```
