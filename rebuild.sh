#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "停止旧容器..."
docker compose down
echo "重新构建镜像（无缓存）..."
docker compose build --no-cache
echo "启动服务..."
docker compose up -d
echo ""
echo "服务已启动，访问地址：http://localhost:$(grep WEB_PORT .env | cut -d= -f2)"
