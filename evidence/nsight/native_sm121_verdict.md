# SM121 Native Verification — Step 3.7 Flash NVFP4

**Date**: 2026-06-04
**Status**: VERIFIED via backend selection + platform capability + runtime proof

## Primary Evidence

### 1. Backend Selection (from vLLM server log)

Both TP ranks selected native Blackwell backends with zero fallback:

```
Worker_TP0: Using 'FLASHINFER_CUTLASS' NvFp4 MoE backend
  out of potential backends: [FLASHINFER_TRTLLM, FLASHINFER_CUTEDSL, FLASHINFER_CUTEDSL_BATCHED, FLASHINFER_CUTLASS, VLLM_CUTLASS, MARLIN, EMULATION]

Worker_TP0: Using 'VLLM_CUTLASS' NvFp4 MoE backend
  out of potential backends: [FLASHINFER_TRTLLM, FLASHINFER_CUTEDSL, FLASHINFER_CUTEDSL_BATCHED, FLASHINFER_CUTLASS, VLLM_CUTLASS, MARLIN, EMULATION]

Worker_TP1: Using 'FLASHINFER_CUTLASS' NvFp4 MoE backend (same set)
Worker_TP1: Using 'VLLM_CUTLASS' NvFp4 MoE backend (same set)

Attention: FLASHINFER on both TP0 and TP1
VIT Attention: FLASH_ATTN
All-reduce: PYNCCL (expected on SM121 — NCCL_SYMM_MEM/QUICK_REDUCE/FLASHINFER/CUSTOM/SYMM_MEM unavailable)

Zero Marlin. Zero emulation. Zero fallback.
```

### 2. Platform Capability Check

```
Device: NVIDIA GB10
SM Capability: (12, 1)  →  SM121 confirmed
is_device_capability_family(120): True  →  vLLM routes to native Blackwell path
is_device_capability_family(100): False →  Not misidentified as datacenter Blackwell
support_deep_gemm(): False  →  DeepGEMM disabled, using CUTLASS directly
```

### 3. Native C Extensions

```
vllm._C: OK
vllm._C_stable_libtorch: OK
vllm._moe_C: OK
```

### 4. Runtime Proof

```
quantization: modelopt_fp4
kv_cache_dtype: fp8
model: Step3p7ForConditionalGeneration (native, not generic fallback)
vLLM: 0.1.dev16944+ge9c8946e7
```

### 5. Inference Evidence

| Test | Result |
|------|--------|
| Text completion | "Paris" — correct factual answer |
| Tool calling | get_weather({"city":" Paris"}) — correct structured output |
| Vision (base64 PNG) | "The image is red" — correct color identification |
| Benchmark tg128 c1 | 14.02 tok/s mean (3 runs) |
| Benchmark random c1 | 13.2 tok/s mean (3 runs) |
| Benchmark random c2 | 27.01 tok/s aggregate (3 runs) |

### 6. GPU Activity During Inference

nsys trace captured at `evidence/nsight/step37_tp2_server_decode.nsys-rep` (3.9MB) shows GPU metrics active during decode workload. nsys version 2025.3.2 on this system does not support `--attach-pids` for per-process CUDA kernel capture; CUDA kernel-level nsys stats are available only when wrapping the server process with nsys at launch time.

## Nsight Limitation

The host nsys (2025.3.2.474) does not support `--attach-pids`. To get per-kernel SM121/SM120 tags in `nsys stats --report cuda_gpu_kern_sum`, the server must be launched wrapped in nsys (requires restarting with nsys as the parent process). This is planned for a follow-up capture but does not block the current verdict — the backend selection logs are the primary gate, and they are unambiguous.

## Verdict

**PASS — Native SM121 NVFP4 execution confirmed.**

The FLASHINFER_CUTLASS and VLLM_CUTLASS backends are native CUTLASS-based FP4 implementations that target SM120/SM121 Blackwell tensor cores. The vLLM runtime correctly identifies SM121 (capability 12,1) as family 120 and routes to the native path. No Marlin or emulation fallback is active on either TP rank.
