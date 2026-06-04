#!/usr/bin/env bash
set -euo pipefail
PORT=${PORT:-30000}
MODEL=${MODEL_NAME:-step3p7}
IMAGE_URL=${VISION_IMAGE_URL:-https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/pipeline-cat-chonk.jpeg}

echo "VISION_SMOKE:"
curl -fsS "http://127.0.0.1:${PORT}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${MODEL}\",
    \"messages\": [{
      \"role\": \"user\",
      \"content\": [
        {\"type\": \"image_url\", \"image_url\": {\"url\": \"${IMAGE_URL}\"}},
        {\"type\": \"text\", \"text\": \"What is shown in this image?\"}
      ]
    }],
    \"max_tokens\": 80,
    \"temperature\": 0
  }" || true
echo ""
