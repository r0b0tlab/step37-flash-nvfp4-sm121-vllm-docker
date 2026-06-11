#!/usr/bin/env python3
"""
Step 3.7 Flash NVFP4 Full Benchmark Campaign
Direct HTTP benchmarking against vLLM OpenAI API.
"""
import json
import time
import os
import sys
import urllib.request
import urllib.error
import concurrent.futures
import statistics
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent
EVIDENCE = BASE / "evidence" / "benchmarks"
EVIDENCE.mkdir(parents=True, exist_ok=True)

PORT = 30000
MODEL = "/home/r0b0tdgx/models/llm/nvfp4/stepfun-ai/Step-3.7-Flash-NVFP4"
URL = f"http://localhost:{PORT}"

def gpu_telemetry():
    """Capture GPU temp, power from host nvidia-smi."""
    try:
        import subprocess
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=temperature.gpu,power.draw,clocks.current.sm,utilization.gpu",
             "--format=csv,noheader,nounits"], text=True, timeout=5
        )
        gpus = []
        for line in out.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 4:
                try:
                    gpus.append({
                        "temp_c": float(parts[0]),
                        "power_w": float(parts[1]),
                        "clock_mhz": int(parts[2]),
                        "util_pct": int(parts[3]),
                    })
                except ValueError:
                    pass
        return gpus
    except:
        return []

def generate_prompt(input_len):
    """Generate a random prompt of approximately input_len tokens."""
    words = "the quick brown fox jumps over the lazy dog and then runs through the forest".split()
    # ~1.3 tokens per word
    n_words = int(input_len / 1.3)
    return " ".join(words[i % len(words)] for i in range(n_words))

def single_request(prompt, max_tokens, request_id=0):
    """Send a single completion request and return timing data."""
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0,
        "stream": False,
    }).encode()
    
    req = urllib.request.Request(
        f"{URL}/v1/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    
    t_start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            body = json.loads(resp.read())
        t_end = time.perf_counter()
        
        usage = body.get("usage", {})
        return {
            "request_id": request_id,
            "status": "ok",
            "latency_s": round(t_end - t_start, 4),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }
    except Exception as e:
        t_end = time.perf_counter()
        return {
            "request_id": request_id,
            "status": "error",
            "error": str(e),
            "latency_s": round(t_end - t_start, 4),
        }

def run_concurrent_bench(name, concurrency, num_prompts, input_len, output_len, mtp_k=None):
    """Run a concurrent benchmark."""
    tag = f"{name}_c{concurrency}"
    if mtp_k:
        tag += f"_mtp{mtp_k}"
    
    print(f"\n{'='*60}")
    print(f"BENCH: {tag}  (c={concurrency}, n={num_prompts}, in={input_len}, out={output_len})")
    print(f"{'='*60}")
    
    prompt = generate_prompt(input_len)
    pre_gpu = gpu_telemetry()
    
    t_wall_start = time.perf_counter()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [
            pool.submit(single_request, prompt, output_len, i)
            for i in range(num_prompts)
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    t_wall_end = time.perf_counter()
    post_gpu = gpu_telemetry()
    
    # Compute stats
    ok_results = [r for r in results if r["status"] == "ok"]
    err_results = [r for r in results if r["status"] != "ok"]
    wall_time = t_wall_end - t_wall_start
    
    if ok_results:
        latencies = [r["latency_s"] for r in ok_results]
        total_completion_tokens = sum(r["completion_tokens"] for r in ok_results)
        total_prompt_tokens = sum(r["prompt_tokens"] for r in ok_results)
        
        # Per-request throughput
        per_req_tok_s = [r["completion_tokens"] / r["latency_s"] for r in ok_results if r["latency_s"] > 0]
        
        stats = {
            "tag": tag,
            "concurrency": concurrency,
            "num_prompts": num_prompts,
            "input_len": input_len,
            "output_len": output_len,
            "mtp_k": mtp_k,
            "ok_count": len(ok_results),
            "err_count": len(err_results),
            "wall_time_s": round(wall_time, 2),
            "aggregate_throughput_tok_s": round(total_completion_tokens / wall_time, 2),
            "aggregate_req_s": round(len(ok_results) / wall_time, 2),
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "latency_p50_s": round(statistics.median(latencies), 4),
            "latency_p90_s": round(sorted(latencies)[int(len(latencies)*0.9)], 4) if len(latencies) > 1 else round(latencies[0], 4),
            "latency_p99_s": round(sorted(latencies)[int(len(latencies)*0.99)], 4) if len(latencies) > 1 else round(latencies[0], 4),
            "latency_min_s": round(min(latencies), 4),
            "latency_max_s": round(max(latencies), 4),
            "per_req_tok_s_mean": round(statistics.mean(per_req_tok_s), 2) if per_req_tok_s else 0,
            "per_req_tok_s_median": round(statistics.median(per_req_tok_s), 2) if per_req_tok_s else 0,
            "pre_gpu": pre_gpu,
            "post_gpu": post_gpu,
        }
    else:
        stats = {
            "tag": tag,
            "concurrency": concurrency,
            "ok_count": 0,
            "err_count": len(err_results),
            "errors": [r.get("error", "") for r in err_results[:3]],
        }
    
    # Print summary
    if ok_results:
        print(f"  ✓ {len(ok_results)}/{num_prompts} ok | {wall_time:.1f}s wall")
        print(f"  Aggregate: {stats['aggregate_throughput_tok_s']:.1f} tok/s, {stats['aggregate_req_s']:.2f} req/s")
        print(f"  Per-req:   {stats['per_req_tok_s_mean']:.1f} tok/s mean")
        print(f"  Latency:   p50={stats['latency_p50_s']:.3f}s  p90={stats['latency_p90_s']:.3f}s  p99={stats['latency_p99_s']:.3f}s")
        if pre_gpu and post_gpu:
            print(f"  GPU:       {pre_gpu[0].get('temp_c', '?')}°C → {post_gpu[0].get('temp_c', '?')}°C, {post_gpu[0].get('power_w', '?')}W")
    else:
        print(f"  ✗ ALL FAILED")
    
    return stats

def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Step 3.7 Flash NVFP4 Benchmark Campaign")
    print(f"Started: {ts}")
    print(f"Config: FP8 KV, MTP K=3, GPU_UTIL=0.70, TP=2, max_model_len=32768")
    print(f"Evidence: {EVIDENCE}")
    
    all_stats = []
    
    # Warmup
    print("\n--- WARMUP ---")
    single_request(generate_prompt(128), 16)
    single_request(generate_prompt(128), 16)
    print("  Warmup done.")
    
    # === PHASE 1: Concurrency sweep (with MTP K=3) ===
    print("\n\n" + "="*80)
    print("PHASE 1: CONCURRENCY SWEEP (MTP K=3)")
    print("="*80)
    
    for c in [1, 2, 3, 4, 5]:
        # tg128
        s = run_concurrent_bench("tg128", c, num_prompts=max(c*3, 6),
                                 input_len=128, output_len=128, mtp_k=3)
        all_stats.append(s)
        
        # random 2k→512
        s = run_concurrent_bench("random_2k512", c, num_prompts=max(c*3, 6),
                                 input_len=2048, output_len=512, mtp_k=3)
        all_stats.append(s)
    
    # === PHASE 2: No-MTP baseline at c1 ===
    print("\n\n" + "="*80)
    print("PHASE 2: NO-MTP BASELINE (requires server restart, using current for comparison)")
    print("NOTE: MTP is active. These results measure with MTP K=3.")
    print("="*80)
    
    # === PHASE 3: Depth sweep ===
    print("\n\n" + "="*80)
    print("PHASE 3: DEPTH SWEEP")
    print("="*80)
    
    for depth in [512, 2048, 8192, 16384]:
        s = run_concurrent_bench(f"depth_{depth}", concurrency=1, num_prompts=3,
                                 input_len=depth, output_len=128, mtp_k=3)
        all_stats.append(s)
    
    # === PHASE 4: Long generation ===
    print("\n\n" + "="*80)
    print("PHASE 4: LONG GENERATION")
    print("="*80)
    
    for out_len in [512, 1024, 2048]:
        s = run_concurrent_bench(f"long_gen_{out_len}", concurrency=1, num_prompts=3,
                                 input_len=512, output_len=out_len, mtp_k=3)
        all_stats.append(s)
    
    # === Save campaign ===
    campaign = {
        "timestamp": ts,
        "model": MODEL,
        "vllm_version": "0.1.dev16944+ge9c8946e7",
        "kv_cache_dtype": "fp8",
        "weight_dtype": "nvfp4 (modelopt_fp4)",
        "gpu_util": 0.70,
        "max_model_len": 32768,
        "tp": 2,
        "mtp_k": 3,
        "spec_method": "step3p5_mtp",
        "backends": {
            "attention": "FLASHINFER",
            "moe": "FLASHINFER_CUTLASS",
            "dense": "VLLM_CUTLASS",
        },
        "enforce_eager": True,
        "nvfp4_kv_tested": True,
        "nvfp4_kv_result": "Unsupported architecture (TllmGenFmhaRunner SM12.1)",
        "results": all_stats,
    }
    
    summary_file = EVIDENCE / f"campaign_{ts}.json"
    with open(summary_file, "w") as f:
        json.dump(campaign, f, indent=2)
    print(f"\n\nCampaign saved: {summary_file}")
    
    # Quick table
    print("\n\n" + "="*80)
    print("RESULTS TABLE")
    print("="*80)
    print(f"{'Tag':35s} {'Agg tok/s':>10s} {'Req/s':>8s} {'Per-req':>10s} {'p50 lat':>10s}")
    print("-" * 80)
    for s in all_stats:
        if s.get("ok_count", 0) > 0:
            print(f"{s['tag']:35s} {s['aggregate_throughput_tok_s']:10.1f} {s['aggregate_req_s']:8.2f} {s['per_req_tok_s_mean']:10.1f} {s['latency_p50_s']:10.4f}")
        else:
            print(f"{s['tag']:35s} {'FAILED':>10s}")

if __name__ == "__main__":
    main()
