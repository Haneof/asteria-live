"""适配器接口协议。"""

from __future__ import annotations

from typing import Iterator, Protocol

from asteria.core.types import (
    AudioSegment,
    CapabilityLevel,
    TimeSpan,
    VideoSegment,
)


class TTSAdapter(Protocol):
    level: CapabilityLevel

    def synthesize(self, text: str, timeline_id: str) -> AudioSegment: ...


class LipSyncAdapter(Protocol):
    level: CapabilityLevel

    def drive(self, audio: AudioSegment, video: VideoSegment) -> VideoSegment: ...


class VideoSourceAdapter(Protocol):
    level: CapabilityLevel

    def read(self, asset_id: str, span: TimeSpan) -> VideoSegment: ...


class StreamAdapter(Protocol):
    level: CapabilityLevel

    def push(self, frames: Iterator[VideoSegment]) -> dict: ...
