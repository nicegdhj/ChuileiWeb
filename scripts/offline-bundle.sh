#!/usr/bin/env bash
set -euo pipefail

OUT="chatbox-private-images.tar"

echo "Building images..."
docker compose build

IMAGES=$(docker compose config --images)
echo "Saving: $IMAGES"
docker save $IMAGES -o "$OUT"
echo "Saved to $OUT ($(du -sh $OUT | cut -f1))"
