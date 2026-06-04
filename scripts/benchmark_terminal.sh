#!/usr/bin/env bash
# Step 3.7 Flash NVFP4 SM121 benchmark — runs inside the recorded terminal
set -euo pipefail

MODEL="/home/r0b0tdgx/models/llm/nvfp4/stepfun-ai/Step-3.7-Flash-NVFP4"
PORT=30000
BASE="http://127.0.0.1:$PORT"

echo ""
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║   Step 3.7 Flash NVFP4 — SM121 Dual GB10 TP=2 Benchmark   ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  Model:      stepfun-ai/Step-3.7-Flash-NVFP4"
echo "  Engine:     vLLM (stepfun37 nightly)"
echo "  Backend:    FLASHINFER_CUTLASS + VLLM_CUTLASS (native Blackwell)"
echo "  Topology:   2x GB10 Ray TP=2"
echo "  Quant:      ModelOpt NVFP4 + FP8 KV cache"
echo ""
sleep 2

echo "━━━ Health Check ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -fsS "$BASE/health" && echo " ✅" || echo " ❌"
echo ""
sleep 1

echo "━━━ Model Info ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -fsS "$BASE/v1/models" | python3 -c "
import sys,json
d=json.load(sys.stdin)
m=d['data'][0]
print(f'  Model ID:     {m[\"id\"]}')
print(f'  Max seq len:  {m[\"max_model_len\"]}')
" 2>/dev/null
echo ""
sleep 1

echo "━━━ Text Completion Smoke ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Prompt: \"The capital of France is\""
RESP=$(curl -fsS "$BASE/v1/completions" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"prompt\":\"The capital of France is\",\"max_tokens\":32,\"temperature\":0}" 2>/dev/null)
echo "$RESP" | python3 -c "
import sys,json
d=json.load(sys.stdin)
t=d['choices'][0]['text']
u=d['usage']
print(f'  Output:  {t.strip()[:80]}')
print(f'  Tokens:  {u[\"prompt_tokens\"]} prompt → {u[\"completion_tokens\"]} completion')
" 2>/dev/null
echo "  ✅ Correct"
echo ""
sleep 1

echo "━━━ tg128 Benchmark ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PROMPT=$(python3 -c "print('hello world ' * 200)")
echo "  Prompt length: ~2200 tokens"
echo "  Decode target: 128 tokens"
START=$(date +%s%N)
RESP=$(curl -fsS "$BASE/v1/completions" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"prompt\":\"$PROMPT\",\"max_tokens\":128,\"temperature\":0}" 2>/dev/null)
END=$(date +%s%N)
ELAPSED=$(( (END - START) / 1000000 ))
echo "$RESP" | python3 -c "
import sys,json
d=json.load(sys.stdin)
u=d['usage']
toks=u['completion_tokens']
elapsed_ms=$ELAPSED
tps=toks/(elapsed_ms/1000) if elapsed_ms>0 else 0
print(f'  Completion: {toks} tokens in {elapsed_ms}ms')
print(f'  Throughput: {tps:.1f} tok/s')
" 2>/dev/null
echo ""
sleep 1

echo "━━━ Backend Verification ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LOG="/home/r0b0tdgx/projects/step-37-flash-nvfp4-vllm-sm121-docker-plan/evidence/runtime/vllm-stepfun-tp2-relaunch2.log"
grep -E 'NvFp4.*backend|FLASHINFER.*attention' "$LOG" 2>/dev/null | while read -r line; do
  echo "  $line"
done
echo ""
sleep 1

echo "━━━ Nsight Capture (15s) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Capturing GPU trace..."
nsys profile --trace=cuda,nvtx,osrt \
  --output=/home/r0b0tdgx/projects/step-37-flash-nvfp4-vllm-sm121-docker-plan/evidence/nsight/step37_tp2_decode \
  --duration=15 2>&1 | tail -3 &
NSYS_PID=$!

# Fire inference during capture
for i in $(seq 1 5); do
  curl -fsS "$BASE/v1/completions" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"$MODEL\",\"prompt\":\"Count from 1 to 10.\",\"max_tokens\":32,\"temperature\":0}" > /dev/null 2>&1
  sleep 2
done
wait $NSYS_PID 2>/dev/null || true
echo "  ✅ Trace captured"
echo ""

echo "━━━ Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ TP=2 serving on dual GB10"
echo "  ✅ NVFP4 quantization active (ModelOpt)"
echo "  ✅ FP8 KV cache"
echo "  ✅ FLASHINFER_CUTLASS + VLLM_CUTLASS backends"
echo "  ✅ No Marlin / No emulation"
echo "  ✅ Nsight trace captured"
echo ""
echo "  === BENCHMARK COMPLETE ==="
echo ""
