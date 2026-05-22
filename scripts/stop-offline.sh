#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if docker compose version &>/dev/null 2>&1; then
    COMPOSE="docker compose"
else
    COMPOSE="docker-compose"
fi
echo "停止并移除容器..."
${COMPOSE} down
echo "完成。"
