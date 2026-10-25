"""基于 FFprobe/FFmpeg 的真实视频源适配器。

能力等级：TESTED（已在当前环境完成可复现测试）。
"""

from __future__ import annotations

import json
import subprocess

from asteria.core.types import CapabilityLevel, TimeSpan, VideoSegment


class FFprobeError(RuntimeError):
    pass


def probe(path: str) -> dict:
    """用 ffprobe 探测视频元数据，返回流信息字典。"""
    cmd = [
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", path,
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=30)
    except subprocess.CalledProcessError as e:
        raise FFprobeError(f"ffprobe 失败: {e.output.decode(errors='replace')[:300]}")
    return json.loads(out.decode())


class FFMpegVideoSource:
    """从本地文件读取视频段，元数据来自真实 ffprobe 探测。"""

    level = CapabilityLevel.TESTED
    is_mock = False

    def read(self, path: str, span: TimeSpan | None = None) -> VideoSegment:
        info = probe(path)
        vstream = next(
            (s for s in info.get("streams", []) if s.get("codec_type") == "video"),
            None,
        )
        if vstream is None:
            raise FFprobeError(f"无视频流: {path}")

        duration_s = float(info.get("format", {}).get("duration", 0) or 0)
        fps_num, _, fps_den = vstream.get("r_frame_rate", "25/1").partition("/")
        fps = float(fps_num) / float(fps_den or 1)
        end_ms = int(duration_s * 1000)
        if span is None:
            span = TimeSpan(start_ms=0, end_ms=end_ms)

        return VideoSegment(
            timeline_id=f"local:{path}",
            span=span,
            fps=fps,
            width=int(vstream.get("width", 0)),
            height=int(vstream.get("height", 0)),
            path=path,
        )
