# vLLM Image Audit — Step 3.7 Flash NVFP4 SM121 Optimization

Captured: 2026-06-03

## Audited images

1. `vllm/vllm-openai:v0.22.0`
2. `vllm/vllm-openai:stepfun37`

## v0.22.0 image findings

- Image ID: sha256:1880a16d095f1037c55538e3768c7b18273964fdd280e2f90bf3557a348866ed
- Runtime versions detected inside image:
  - vLLM 0.22.0
  - torch 2.11.0+cu130
- Required vLLM C/native imports succeeded:
  - vllm._C
  - vllm._C_stable_libtorch
  - vllm._moe_C
- `torch.ops._C.cutlass_scaled_mm_supports_fp4` attribute was present.
- However, calling `cutlass_scaled_mm_supports_fp4(120)` or `(121)` failed in this image with missing custom op binding on this run.
- Fallback artifacts scanned in image:
  - _vllm_fa2_C found
  - _vllm_fa3_C found
  - marlin artifacts not found

Conclusion:
`vllm/vllm-openai:v0.22.0` is usable as a stable baseline sanity reference, but it is not sufficient as a strict native-only publishable artifact for this project.

## stepfun37 image findings

- Runtime versions detected inside image:
  - vLLM 0.1.dev16944+ge9c8946e7
  - torch 2.11.0+cu130
- Required vLLM C/native imports succeeded.
- Model registry source file contained:
  - Step3p7
  - Step3p5
  - Step3p7ForConditionalGeneration
- `torch.ops._C.cutlass_scaled_mm_supports_fp4` attribute was present.
- Official recipe reference image is therefore useful for Step3p7 compatibility and upstream behavior comparison.

Conclusion:
`vllm/vllm-openai:stepfun37` is the stronger upstream reference image for Step3p7 serving. The strict r0b0tlab publication image still needs to be built from chosen source with no-fallback packaging and SM12x evidence gates.
