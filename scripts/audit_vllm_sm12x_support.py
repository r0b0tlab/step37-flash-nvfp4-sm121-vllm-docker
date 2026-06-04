import pathlib
patterns = [
    'FlashInfer b12x MoE + FP4 GEMM for SM120/121',
    'per-tensor FP8 CUTLASS on SM12.1',
    'NVFP4 Cutlass linear path',
    'padded NVFP4 quant kernel',
    'ModelOpt W4A16 NVFP4 fused MoE',
    'TRTLLM NVFP4 MoE routing fix',
]
text = pathlib.Path('/workspace/vllm/CHANGELOG.md').read_text(errors='ignore') if pathlib.Path('/workspace/vllm/CHANGELOG.md').exists() else ''
found=[]
for pat in patterns:
    found.append((pat, pat in text))
print(found)
print('pass', all(ok for _,ok in found))
