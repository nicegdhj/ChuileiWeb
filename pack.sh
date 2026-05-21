#!/usr/bin/env bash
# 一键打包离线部署包（在开发机有公网的环境执行）
set -e
cd "$(dirname "$0")"

VERSION=${VERSION:-$(date +%Y%m%d)}
BUNDLE_NAME="chatbox-bundle-${VERSION}"
BUNDLE_DIR="/tmp/${BUNDLE_NAME}"
IMAGE_API="chatbox-private-api:latest"
IMAGE_WEB="chatbox-private-web:latest"

echo "=== [1/4] 构建 Docker 镜像（无缓存）==="
docker compose build --no-cache

echo "=== [2/4] 导出镜像为 tar ==="
rm -rf "${BUNDLE_DIR}"
mkdir -p "${BUNDLE_DIR}/images" "${BUNDLE_DIR}/data/db" "${BUNDLE_DIR}/data/uploads"

docker save "${IMAGE_API}" -o "${BUNDLE_DIR}/images/api.tar"
echo "  api.tar 导出完成（$(du -sh "${BUNDLE_DIR}/images/api.tar" | cut -f1)）"

docker save "${IMAGE_WEB}" -o "${BUNDLE_DIR}/images/web.tar"
echo "  web.tar 导出完成（$(du -sh "${BUNDLE_DIR}/images/web.tar" | cut -f1)）"

echo "=== [3/4] 复制配置文件 ==="
cp scripts/docker-compose.prod.yml "${BUNDLE_DIR}/docker-compose.yml"
cp .env.template                   "${BUNDLE_DIR}/.env.template"
cp scripts/deploy-offline.sh       "${BUNDLE_DIR}/deploy.sh"
cp scripts/stop-offline.sh         "${BUNDLE_DIR}/stop.sh"
chmod +x "${BUNDLE_DIR}/deploy.sh" "${BUNDLE_DIR}/stop.sh"

echo "=== [4/4] 打 tar.gz 包 ==="
OUTPUT="${BUNDLE_NAME}.tar.gz"
tar -czf "${OUTPUT}" -C /tmp "${BUNDLE_NAME}"
rm -rf "${BUNDLE_DIR}"

echo ""
echo "打包完成：${OUTPUT}"
echo "文件大小：$(du -sh "${OUTPUT}" | cut -f1)"
echo ""
echo "使用方法："
echo "  1. 将 ${OUTPUT} 拷贝到目标机器"
echo "  2. tar -xzf ${OUTPUT} && cd ${BUNDLE_NAME}"
echo "  3. cp .env.template .env  # 编辑 .env 填写 LLM 配置"
echo "  4. bash deploy.sh"
