#!/usr/bin/env python3
"""抖音直播间录制器（基于 DouyinLiveRecorder 的 spider 模块）。

用法:
  python3 scripts/record_douyin.py <分享链接或直播间URL> [--duration 秒数] [--watch]

- 默认：探测一次，开播则录制 --duration 秒（默认 60s）
- --watch：常驻监控，未开播每 60s 轮询，开播自动录制
"""

import argparse
import asyncio
import os
import subprocess
import sys
import time

sys.path.insert(0, "/opt/DouyinLiveRecorder")
from src import spider  # noqa: E402

OUT_DIR = "/workspace/data/raw/livestreams"


async def resolve_and_probe(url: str) -> str:
    """解析分享短链，返回带完整参数的最终 URL。"""
    if "v.douyin.com" in url:
        url = subprocess.check_output(
            ["curl", "-sI", "-L", url, "-o", "/dev/null", "-w", "%{url_effective}"],
            timeout=30,
        ).decode()
    return url


async def probe(url: str) -> dict:
    return await spider.get_douyin_app_stream_data(url)


def record(stream_url: str, out_path: str, duration: int) -> bool:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-user_agent", "Mozilla/5.0",
         "-i", stream_url, "-t", str(duration), "-c", "copy", out_path],
        capture_output=True, text=True, timeout=duration + 60,
    )
    if r.returncode == 0 and os.path.exists(out_path):
        print(f"录制完成: {out_path} ({os.path.getsize(out_path)} bytes)")
        return True
    print(f"录制失败: {r.stderr[-300:]}", file=sys.stderr)
    return False


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="直播间分享链接或地址")
    ap.add_argument("--duration", type=int, default=60, help="录制秒数")
    ap.add_argument("--watch", action="store_true", help="常驻监控，开播自动录")
    args = ap.parse_args()

    resolved_url = await resolve_and_probe(args.url)

    while True:
        d = await probe(resolved_url)
        name = d.get("anchor_name") or "unknown"
        title = d.get("title") or ""
        stream = d.get("record_url")
        print(f"[{time.strftime('%H:%M:%S')}] 主播: {name} | 标题: {title} | 开播: {bool(stream)}")

        if stream:
            ts = time.strftime("%Y%m%d_%H%M%S")
            safe = "".join(c for c in name if c.isalnum())[:20]
            out = f"{OUT_DIR}/{safe}_{ts}.mp4"
            record(stream, out, args.duration)
            if not args.watch:
                return 0
        if not args.watch:
            print("未开播。加 --watch 可常驻监控。")
            return 1
        await asyncio.sleep(60)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()) or 0)
