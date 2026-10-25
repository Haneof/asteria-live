"""适配器层：TTS / 口型 / 视频源 / 推流。

所有模型与平台能力经适配器接入；Mock 实现仅用于验证接口与状态机，
不得冒充真实模型能力。
"""

from asteria.adapters.base import (
    LipSyncAdapter,
    StreamAdapter,
    TTSAdapter,
    VideoSourceAdapter,
)

__all__ = [
    "TTSAdapter",
    "LipSyncAdapter",
    "VideoSourceAdapter",
    "StreamAdapter",
]
