# AGENTS.md — Step 3.7 Flash NVFP4 SM121

Guidance for agents and humans working on StepFun `stepfun-ai/Step-3.7-Flash-NVFP4` on dual GB10 / Blackwell SM121.

## What this repo is
A validated, plug-and-play TP=2 serving environment for Step 3.7 Flash NVFP4 on dual NVIDIA DGX Spark (GB10/SM121) with vLLM and Ray. Proven native Blackwell CUTLASS execution with zero Marlin/emulation fallback.

## The one rule that matters most
**Do not publish fallback/emulation results as SM121-optimized native results.**
If Marlin, emulation, or CPU fallback is selected, the run is invalid.

## Source of truth
- Model: `stepfun-ai/Step-3.7-Flash-NVFP4` (198B total, 11B active, 288 experts, NVFP4)
- Serving: vLLM with Ray TP=2 over QSFP
- Image: `step37-stepfun-ray:arm64` (vLLM 0.1.dev16944)
- Quantization: modelopt_fp4, FP8 KV cache

## Required checks before claiming native SM121
1. Backend selection log shows FLASHINFER_CUTLASS + VLLM_CUTLASS (not Marlin/emulation)
2. `torch.cuda.get_device_capability()` returns (12, 1)
3. `is_device_capability_family(120)` returns True
4. All native imports pass: vllm._C, vllm._C_stable_libtorch, vllm._moe_C
5. Text, tool-call, and vision smoke tests pass
6. Nsight trace shows NCCL all-reduces and CUTLASS/CCCL kernels active

## Launch recipe (dual GB10, TP=2)
```bash
# Start Ray head (node1)
docker run -d --name step37-vllm --gpus all --ipc=host --network=host \
  --entrypoint bash -v /home/r0b0tdgx:/home/r0b0tdgx:ro \
  step37-stepfun-ray:arm64 -lc "ray start --head --node-ip-address=192.168.100.10 --port=6379 --block"

# Start Ray worker (node2)
ssh node2 "docker run -d --name step37-vllm-worker --gpus all --ipc=host --network=host \
  --entrypoint bash -v /home/r0b0tdgx:/home/r0b0tdgx:ro \
  step37-stepfun-ray:arm64 -lc 'ray start --address=192.168.100.10:6379 --node-ip-address=192.168.100.11 --block'"

# Launch vLLM inside head container
docker exec -d step37-vllm bash -lc '
export NCCL_SOCKET_IFNAME=enp1s0f0np0 GLOO_SOCKET_IFNAME=enp1s0f0np0 TP_SOCKET_IFNAME=enp1s0f0np0 VLLM_HOST_IP=192.168.100.10
python3 -m vllm.entrypoints.openai.api_server \
  --model /home/r0b0tdgx/models/llm/nvfp4/stepfun-ai/Step-3.7-Flash-NVFP4 \
  --host 0.0.0.0 --port 30000 \
  --trust-remote-code --tensor-parallel-size 2 --distributed-executor-backend ray \
  --disable-custom-all-reduce --quantization modelopt --kv-cache-dtype fp8 \
  --disable-cascade-attn --gpu-memory-utilization 0.70 --max-model-len 8192 \
  --max-num-batched-tokens 8192 --max-num-seqs 4 \
  --reasoning-parser step3p5 --tool-call-parser step3p5 --enable-auto-tool-choice \
  --enforce-eager
'
```

## Why each flag exists
- `--tensor-parallel-size 2`: dual GB10 TP=2
- `--distributed-executor-backend ray`: Ray for cross-node TP
- `--disable-custom-all-reduce`: SM121 uses PYNCCL (NCCL_SYMM_MEM unavailable)
- `--quantization modelopt`: NVFP4 modelopt_fp4 quantization
- `--kv-cache-dtype fp8`: FP8 KV cache (model default)
- `--disable-cascade-attn`: REQUIRED — Step 3.7 uses hybrid sliding-window attention
- `--enforce-eager`: REQUIRED — Triton JIT + CUDA graphs cause RPC timeout on first run
- `--reasoning-parser step3p5 --tool-call-parser step3p5`: Step 3.5/3.7 tool call format
- `--gpu-memory-utilization 0.70`: conservative for 129GB model on 121GB nodes

## Forbidden changes
- Do NOT remove `--disable-cascade-attn` (breaks hybrid attention)
- Do NOT remove `--enforce-eager` without testing (causes RPC timeout)
- Do NOT switch to Marlin/emulation and claim SM121
- Do NOT increase GPU util above 0.85 without testing OOM
- Do NOT set `--kv-cache-dtype` to anything other than fp8 without model card check

## Performance baseline
| Benchmark | tok/s | Notes |
|-----------|-------|-------|
| tg128 c1 | 14.02 | Single stream decode |
| random c1 | 13.2 | 2048→1024 tokens |
| random c2 | 27.01 | 2 concurrent, aggregate |

## Troubleshooting
- Server won't start: check Ray status (`docker exec step37-vllm ray status`)
- RPC timeout: ensure `--enforce-eager` is set
- OOM: reduce `--gpu-memory-utilization` or `--max-model-len`
- PYNCCL warning: expected on SM121, not an error
- Vision 500 error: check image URL accessibility from container
