# Docker Instructions — Step 3.7 Flash NVFP4 SM121 Optimization

## Reference images currently used for validation

1. vLLM stable reference:
   - `vllm/vllm-openai:v0.22.0`

2. Upstream Step3p7 reference:
   - `vllm/vllm-openai:stepfun37`

These are used for upstream behavior validation and compatibility checks. They are not automatically the final publishable image.

## Current recommended local smoke path

Use the local stepfun37 image once the full model download is complete:

```bash
./docker/run_single_node_smoke.sh
```

## Planned dual-GB10 TP=2 path

```bash
./docker/run_worker_tp2.sh
./docker/run_head_tp2.sh
./scripts/ray_health.sh
```

## Current blockers

- Full model download must complete.
- Hostname mapping for `gn100-89ac` must be restored on the local node.
- Final strict native-only r0b0tlab image is not yet published.
