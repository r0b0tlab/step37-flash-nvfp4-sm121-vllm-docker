# Step3.7 NVFP4 TP=2 Launch Failure — Memory + Remote Path

Captured: 2026-06-04

## Evidence source
`/home/r0b0tdgx/projects/step-37-flash-nvfp4-vllm-sm121-docker-plan/evidence/runtime/vllm-stepfun-tp2-launch.log`

## What succeeded
- Dual-node Ray came up on both nodes.
- vLLM on the head node resolved the target architecture as `Step3p7ForConditionalGeneration`.
- Engine config correctly detected `quantization=modelopt_fp4` and `kv_cache_dtype=fp8`.

## What failed

### 1. CUDA memory reservation failed on the head node
Key line:

```text
ValueError: Free memory on device cuda:0 (82.96/121.69 GiB) on startup is less than desired GPU memory utilization (0.7, 85.18 GiB).
```

Interpretation:
The first TP rank attempted to reserve 70% of GPU memory, but only 82.96 GiB was available at startup. This is a memory environment issue, not a model architecture issue.

### 2. Remote worker could not load local model path
Key line:

```text
Repo id must be in the form 'repo_name' or 'namespace/repo_name': '/home/r0b0tdgx/models/llm/nvfp4/stepfun-ai/Step-3.7-Flash-NVFP4'
```

Interpretation:
The node2 Ray worker did not successfully treat the model path as a valid local directory. This is likely a missing bind mount / missing local model directory issue on node2, so vLLM fell back to repo-style path handling and failed.

## Conclusion
The current TP=2 blocker is operational: head-node available GPU memory was too low for `gpu_memory_utilization=0.7`, and the node2 worker model path was not available locally.
