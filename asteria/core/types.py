"""时间轴与共享类型（ASTERIA-SYNC）。

统一内部时间轴使用整数毫秒；原始媒体 PTS 与 time_base 保留，不与毫秒轴混用。
区间统一为 [start_ms, end_ms) 半开区间。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator


class CapabilityLevel(Enum):
    """模型能力分级，禁止混淆。"""

    DOCUMENTED = "documented"
    TESTED = "tested"
    PRODUCTION_VALIDATED = "production_validated"


@dataclass(frozen=True)
class TimeSpan:
    """半开时间区间 [start_ms, end_ms)。"""

    start_ms: int
    end_ms: int

    def __post_init__(self) -> None:
        if self.start_ms < 0:
            raise ValueError("start_ms 不能为负")
        if self.end_ms < self.start_ms:
            raise ValueError("end_ms 必须 >= start_ms")

    @property
    def duration_ms(self) -> int:
        return self.end_ms - self.start_ms

    def contains(self, ms: int) -> bool:
        return self.start_ms <= ms < self.end_ms


@dataclass(frozen=True)
class MediaTimestamp:
    """原始媒体时间戳：保留 PTS 与 time_base，同时给出换算毫秒。"""

    pts: int
    time_base_num: int
    time_base_den: int
    ms: int


@dataclass
class AudioSegment:
    """音频段引用（数据以字节或文件路径形式存在）。"""

    timeline_id: str
    span: TimeSpan
    sample_rate: int
    data: bytes | None = None
    path: str | None = None


@dataclass
class VideoSegment:
    """视频段引用。"""

    timeline_id: str
    span: TimeSpan
    fps: float
    width: int
    height: int
    path: str | None = None
    frames: Iterator[bytes] | None = None
