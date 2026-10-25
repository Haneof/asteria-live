"""G2 闭环运行脚本。"""

import argparse
import json
import sys

from asteria.core.logging import setup_logging
from asteria.pipeline.loop import LiveLoop


def main() -> int:
    ap = argparse.ArgumentParser(description="Asteria G2 最小实时闭环")
    ap.add_argument("--video", required=True, help="本地动作视频路径")
    ap.add_argument("--topic", default="测试商品", help="话术主题")
    ap.add_argument("--timeline", default="g2-run", help="timeline_id")
    args = ap.parse_args()

    setup_logging("INFO")
    loop = LiveLoop()
    out_path, m = loop.run(args.video, args.topic, args.timeline)

    print(json.dumps({
        "output": out_path,
        "video_duration_ms": m.video_duration_ms,
        "audio_duration_ms": m.audio_duration_ms,
        "output_duration_ms": m.output_duration_ms,
        "av_offset_ms": m.av_offset_ms,
        "resolution": f"{m.width}x{m.height}",
        "real": m.real_components,
        "mock": m.mock_components,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
