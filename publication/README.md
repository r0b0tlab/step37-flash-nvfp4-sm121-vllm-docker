# Step 3.7 Flash NVFP4 SM121 Optimization Workspace

Author: @mr-r0b0t — r0b0tlab

This workspace is the active optimization and publication scaffold for `stepfun-ai/Step-3.7-Flash-NVFP4` on dual NVIDIA GB10 / SM121 Blackwell hardware with vLLM.

## Current status

Status: **IN PROGRESS**

What is done:
- Dual GB10 preflight captured.
- Official upstream images audited:
  - `vllm/vllm-openai:v0.22.0`
  - `vllm/vllm-openai:stepfun37`
- Step3p7 registry support confirmed inside `stepfun37` image.
- Model quant metadata verified from HF checkpoint metadata.
- Local publication scaffolding created for TP=2 Ray scripts and evidence capture.

What remains before GO:
1. Download the full `stepfun-ai/Step-3.7-Flash-NVFP4` model.
2. Restore hostname/route mapping for worker node `gn100-89ac`.
3. Start Ray cleanly on both GB10 nodes.
4. Run TP=2 server smoke and correctness checks.
5. Capture Nsight SM121/SM120 native-kernel evidence.
6. Build/validate strict r0b0tlab image.
7. Publish final HTML artifact, AGENTS.md, README, and image digest.

## Primary artifacts

- Active plan: `wiki/projects/step-37-flash-nvfp4-vllm-sm121-docker-plan.md`
- Review: `wiki/projects/step-37-flash-nvfp4-vllm-sm121-docker-plan-review.md`
- Evidence workspace: `evidence/`
- Publication workspace: `publication/`

## Compatible devices

Primary tested target:
- 2x NVIDIA GB10 / DGX Spark, SM121, 128 GB unified memory per node, QSFP fabric.

Do not claim optimized native NVFP4 Blackwell performance on non-Blackwell hardware.
