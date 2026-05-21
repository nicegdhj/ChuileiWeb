#!/usr/bin/env bash
# 离线部署脚本 —— 在目标机器（无公网）上执行
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${SCRIPT_DIR}"

# ---- 环境检查 ----
echo "=== [1/4] 检查环境 ==="
if ! command -v docker &>/dev/null; then
    echo "ERROR: 未检测到 docker，请先安装 Docker Engine"
    echo "  参考：https://docs.docker.com/engine/install/"
    exit 1
fi
if ! docker compose version &>/dev/null 2>&1; then
    echo "ERROR: 未检测到 docker compose 插件"
    echo "  参考：https://docs.docker.com/compose/install/"
    exit 1
fi

# ---- 加载镜像 ----
echo "=== [2/4] 加载镜像（首次约需 1-2 分钟）==="
docker load -i images/api.tar
docker load -i images/web.tar
echo "  镜像加载完成"

# ---- 初始化配置 ----
echo "=== [3/4] 初始化配置 ==="
if [ ! -f .env ]; then
    cp .env.template .env
    echo ""
    echo "  已生成 .env 文件，请先编辑填写 LLM 地址和密钥："
    echo "    vi .env"
    echo ""
    echo "  编辑完成后再次执行本脚本：bash deploy.sh"
    exit 0
fi
mkdir -p data/db data/uploads

# ---- 启动服务 ----
echo "=== [4/4] 启动服务 ==="
docker compose up -d

WEB_PORT=$(grep '^WEB_PORT' .env | cut -d= -f2 | tr -d ' \r')
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "<本机IP>")
echo ""
echo "================================================"
echo "  服务已启动！"
echo "  访问地址：http://${LOCAL_IP}:${WEB_PORT:-8088}/chuilei/chat"
echo "================================================"
