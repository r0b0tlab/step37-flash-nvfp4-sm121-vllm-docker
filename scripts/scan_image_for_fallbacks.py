import pathlib, site, json
patterns=['*_vllm_fa2_C*.so','*_vllm_fa3_C*.so','*marlin*.so']
roots=[pathlib.Path('/opt/vllm-src'), *[pathlib.Path(p) for p in __import__('site').getsitepackages()], pathlib.Path('/usr/local/lib')]
hits={}
for pat in patterns:
    hits[pat]=[]
    for r in roots:
        if r.exists():
            hits[pat].extend(str(p) for p in r.rglob(pat))
print(json.dumps(hits, indent=2))
print('pass', all(len(v)==0 for v in hits.values()))
