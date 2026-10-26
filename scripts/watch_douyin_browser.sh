#!/usr/bin/env bash
# 浏览器版抖音直播监控：用 playwright-cli 驱动真实 Chromium，
# 每 90s 检查直播间页面，出现 <video> 即提取流地址并用 ffmpeg 录制。
set -u
URL="$1"
DURATION="${2:-120}"
OUT_DIR="/workspace/data/raw/livestreams"
mkdir -p "$OUT_DIR"

cd /root
echo "[watch] 启动监控: $URL (录制 ${DURATION}s/次)"

while true; do
  # 确保浏览器会话在
  if ! playwright-cli eval '1' >/dev/null 2>&1; then
    playwright-cli open "$URL" --config=/root/playwright-cli.json >/dev/null 2>&1
    sleep 12
  else
    playwright-cli goto "$URL" >/dev/null 2>&1
    sleep 10
  fi

  # 质询页检测
  TITLE=$(playwright-cli eval 'document.title' 2>/dev/null | grep -o '"[^"]*"' | tr -d '"' | head -1)
  if [[ "$TITLE" == *"验证码"* ]]; then
    echo "[$(date +%H:%M:%S)] 触发验证码，等待人工/跳过"
    sleep 60
    continue
  fi

  NV=$(playwright-cli eval 'document.querySelectorAll("video").length' 2>/dev/null | grep -o '[0-9]*' | head -1)
  if [[ "${NV:-0}" -ge 1 ]]; then
    echo "[$(date +%H:%M:%S)] 检测到播放器! 提取流地址..."
    SRC=$(playwright-cli eval 'JSON.stringify(Array.from(document.querySelectorAll("video")).map(v=>v.src||"").filter(Boolean))' 2>/dev/null | tr -d '"' | head -c 2000)
    echo "[$(date +%H:%M:%S)] video src: ${SRC:0:120}"
    # 从页面拿到的可能是 blob:，需要从 network 层拿真实流地址：改用 performance entries
    REAL=$(playwright-cli eval 'JSON.stringify(performance.getEntriesByType("resource").map(e=>e.name).filter(n=>/flv|hls|m3u8|pull|\.mp4/.test(n)).slice(-3))' 2>/dev/null | head -c 2000)
    echo "[$(date +%H:%M:%S)] 资源地址: ${REAL:0:300}"
    TS=$(date +%Y%m%d_%H%M%S)
    # 若拿到 http 流地址则录制
    STREAM=$(echo "$REAL" | grep -oE 'https?://[^"]+' | head -1)
    if [ -n "$STREAM" ]; then
      ffmpeg -y -v error -user_agent "Mozilla/5.0" -i "$STREAM" -t "$DURATION" -c copy "$OUT_DIR/live_${TS}.mp4" \
        && echo "[$(date +%H:%M:%S)] 录制完成: live_${TS}.mp4"
    fi
    sleep 120
  else
    echo "[$(date +%H:%M:%S)] 未开播"
    sleep 90
  fi
done
