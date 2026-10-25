"""Mock 适配器：用于验证接口与状态机，非真实模型能力。"""

from __future__ import annotations

from typing import Iterator

from asteria.core.types import (
    AudioSegment,
    CapabilityLevel,
    TimeSpan,
    VideoSegment,
)


class MockTTS:
    """把文本回显为占位音频。level 标记为 DOCUMENTED 以下、明确是 Mock。"""

    level = CapabilityLevel.DOCUMENTED
    is_mock = True

    def synthesize(self, text: str, timeline_id: str) -> AudioSegment:
        return AudioSegment(
            timeline_id=timeline_id,
            span=TimeSpan(start_ms=0, end_ms=1000),
            sample_rate=24000,
            data=("mock:" + text).encode("utf-8"),
        )


class MockLipSync:
    level = CapabilityLevel.DOCUMENTED
    is_mock = True

    def drive(self, audio: AudioSegment, video: VideoSegment) -> VideoSegment:
        return VideoSegment(
            timeline_id=video.timeline_id,
            span=video.span,
            fps=video.fps,
            width=video.width,
            height=video.height,
            path=video.path,
        )


class MockVideoSource:
    level = CapabilityLevel.DOCUMENTED
    is_mock = True

    def read(self, asset_id: str, span: TimeSpan) -> VideoSegment:
        return VideoSegment(
            timeline_id=asset_id,
            span=span,
            fps=25.0,
            width=1280,
            height=720,
            path=None,
        )


class MockStream:
    level = CapabilityLevel.DOCUMENTED
    is_mock = True

    def push(self, frames: Iterator[VideoSegment]) -> dict:
        n = sum(1 for _ in frames)
        return {"pushed_frames": n, "target": "mock"}
