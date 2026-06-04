#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PORT=${PORT:-30000}
URL="http://127.0.0.1:${PORT}/health"
echo "Waiting for $URL"
for i in $(seq 1 120); do
  if curl -fsS "$URL" >/tmp/step37-health.json 2>/tmp/step37-health.err; then
    echo "HEALTH_OK"
    cat /tmp/step37-health.json
    exit 0
  fi
  sleep 5
done
echo "HEALTH_TIMEOUT"
cat /tmp/step37-health.err 2>/dev/null || true
exit 1
