#!/usr/bin/env bash
set -euo pipefail
PORT=${PORT:-30000}
MODEL=${MODEL_NAME:-step3p7}

echo "HEALTH:"
curl -fsS "http://127.0.0.1:${PORT}/health" || true
echo ""
echo "MODELS:"
curl -fsS "http://127.0.0.1:${PORT}/v1/models" || true
echo ""

echo "CHAT_SMOKE:"
curl -fsS "http://127.0.0.1:${PORT}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${MODEL}\",
    \"messages\": [{\"role\":\"user\",\"content\":\"What is the capital of France?\"}],
    \"max_tokens\": 64,
    \"temperature\": 0
  }" || true
echo ""
