"""Mock TTS：生成真实 WAV 音频流（正弦波占位，非真实语音）。

能力等级：仅为 Mock，不代表真实 TTS 语音质量。
音频流本身是合法 WAV，可供下游合成与时间戳测量使用。
"""

from __future__ import annotations

import io
import math
import struct
import wave

from asteria.core.types import AudioSegment, CapabilityLevel, TimeSpan

SAMPLE_RATE = 24000


class MockTTSWav:
    is_mock = True
    level = CapabilityLevel.DOCUMENTED

    def __init__(self, freq: float = 440.0) -> None:
        self.freq = freq

    def synthesize(self, text: str, timeline_id: str) -> AudioSegment:
        # 时长按文本长度估算：每字符 80ms，至少 500ms（Mock 规则）。
        duration_ms = max(500, len(text) * 80)
        n = int(SAMPLE_RATE * duration_ms / 1000)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SAMPLE_RATE)
            frames = bytearray()
            for i in range(n):
                t = i / SAMPLE_RATE
                # 正弦波 + 简单淡入淡出，避免爆音
                amp = min(1.0, t * 20) * min(1.0, (n - i) / (SAMPLE_RATE * 0.05))
                v = int(amp * 0.3 * 32767 * math.sin(2 * math.pi * self.freq * t))
                frames += struct.pack("<h", v)
            w.writeframes(bytes(frames))
        return AudioSegment(
            timeline_id=timeline_id,
            span=TimeSpan(start_ms=0, end_ms=duration_ms),
            sample_rate=SAMPLE_RATE,
            data=buf.getvalue(),
        )
