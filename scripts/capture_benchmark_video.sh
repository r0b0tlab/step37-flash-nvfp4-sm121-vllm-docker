#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/r0b0tdgx/projects/step-37-flash-nvfp4-vllm-sm121-docker-plan
OUT=${1:-$ROOT/evidence/video/step37_benchmark.mp4}
DUR=${2:-180}
DISP=${3:-182}

mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"

echo "=== Step 3.7 NVFP4 Benchmark Video Capture ==="
echo "  Output:   $OUT"
echo "  Duration: ${DUR}s"
echo "  Display:  :$DISP"

# Start Xvfb
Xvfb ":$DISP" -screen 0 1920x1080x24 -ac +extension GLX +render -noreset >/tmp/step37_xvfb.log 2>&1 &
XV=$!
export DISPLAY=":$DISP.0"
sleep 1

# Open xterm with the benchmark script
xterm -geometry 120x35+10+10 -title "Step 3.7 Flash NVFP4 — SM121 Benchmark" \
  -fa "Monospace" -fs 14 \
  -bg black -fg green \
  -e bash -lc "cd $ROOT; bash scripts/benchmark_terminal.sh; exec bash" &
TERM_PID=$!
sleep 3

# Record with ffmpeg
ffmpeg -y -video_size 1920x1080 -framerate 30 -f x11grab -i ":$DISP.0+0,0" \
  -t "$DUR" \
  -vf "drawbox=x=0:y=0:w=1920:h=56:color=0x050510@0.96:t=fill,drawtext=text='r0b0tlab  |  Step 3.7 Flash NVFP4  |  SM121 Dual GB10 TP=2':fontcolor=0x00e5ff:fontsize=28:x=24:y=18,drawtext=text='@mr-r0b0t':fontcolor=0xf0f0f5@0.60:fontsize=14:x=w-tw-20:y=h-28" \
  -c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p -movflags +faststart \
  "$OUT" >/tmp/step37_ffmpeg.log 2>&1

# Cleanup
kill $TERM_PID $XV 2>/dev/null || true

echo "=== Capture complete ==="
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,duration -of default=noprint_wrappers=1 "$OUT" 2>/dev/null || true
du -h "$OUT"
