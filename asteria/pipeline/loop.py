"""G2 最小实时闭环编排。

真实/Mock 边界：
- 视频读取（FFprobe 探测）：真实
- 话术（模板）：Mock，LLM 未接入
- TTS（正弦波 WAV）：音频流真实，语音内容 Mock
- 口型：Mock 直通，真实口型模型未接入
- 合成（FFmpeg h264+aac mux）：真实
- 指标（ffprobe 实测输出、音画时长偏差）：真实测量
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from asteria.adapters.ffmpeg_source import FFMpegVideoSource
from asteria.adapters.mock import MockLipSync
from asteria.adapters.mock_tts_wav import MockTTSWav
from asteria.core.logging import get_logger
from asteria.core.types import AudioSegment, TimeSpan, VideoSegment

log = get_logger("asteria.loop")


class MockScript:
    """模板话术生成器（Mock，LLM 未接入）。"""

    is_mock = True

    def generate(self, topic: str) -> str:
        return f"欢迎来到直播间，今天给大家带来的是{topic}，品质保证，福利满满！"


@dataclass
class LoopMetrics:
    video_duration_ms: int = 0
    audio_duration_ms: int = 0
    output_duration_ms: int = 0
    av_offset_ms: int = 0
    width: int = 0
    height: int = 0
    fps: float = 0.0
    real_components: list = field(default_factory=list)
    mock_components: list = field(default_factory=list)


def _probe_duration_ms(path: str) -> int:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        timeout=30,
    ).decode().strip()
    return int(float(out) * 1000)


def _pick_h264_encoder() -> str:
    """按可用性选择 H.264 软编码器（沙箱无 GPU 时回落 openh264）。"""
    out = subprocess.check_output(
        ["ffmpeg", "-hide_banner", "-encoders"], timeout=15
    ).decode(errors="replace")
    for name in ("libx264", "libopenh264"):
        if f" {name} " in out:
            return name
    raise RuntimeError("无可用 H.264 软编码器")


class LiveLoop:
    """最小实时闭环：读取视频 → 话术 → TTS → 口型(Mock) → 合成 → 指标。"""

    def __init__(self, output_dir: str = "data/output") -> None:
        self.source = FFMpegVideoSource()
        self.script = MockScript()
        self.tts = MockTTSWav()
        self.lipsync = MockLipSync()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, video_path: str, topic: str, timeline_id: str) -> tuple[str, LoopMetrics]:
        t0 = time.monotonic()
        # 1. 读取本地动作视频（真实 ffprobe）
        video: VideoSegment = self.source.read(video_path)
        log.info("视频读取完成: %sx%s @%sfps %sms",
                 video.width, video.height, video.fps, video.span.duration_ms)

        # 2. 生成话术（Mock）
        text = self.script.generate(topic)

        # 3. TTS 音频（Mock 语音 + 真实 WAV 流）
        audio: AudioSegment = self.tts.synthesize(text, timeline_id)

        # 4. 口型驱动（Mock 直通；真实实现必须以实际播放音频为输入）
        out_video = self.lipsync.drive(audio, video)

        # 5. FFmpeg 合成音视频（真实 mux，AAC 编码音频）
        audio_path = self.output_dir / f"{timeline_id}_audio.wav"
        audio_path.write_bytes(audio.data)
        out_path = self.output_dir / f"{timeline_id}.mp4"
        venc = _pick_h264_encoder()
        subprocess.check_call(
            ["ffmpeg", "-y", "-v", "error",
             "-i", out_video.path,
             "-i", str(audio_path),
             "-c:v", venc, "-crf", "23",
             "-c:a", "aac", "-b:a", "128k",
             "-shortest", "-movflags", "+faststart",
             str(out_path)],
            timeout=300,
        )

        # 6. 指标（真实测量）
        m = LoopMetrics()
        m.video_duration_ms = out_video.span.duration_ms
        m.audio_duration_ms = audio.span.duration_ms
        m.output_duration_ms = _probe_duration_ms(str(out_path))
        m.av_offset_ms = abs(m.output_duration_ms - min(m.video_duration_ms, m.audio_duration_ms))
        m.width, m.height, m.fps = out_video.width, out_video.height, out_video.fps
        m.real_components = ["ffprobe_video_read", "ffmpeg_mux", "metrics"]
        m.mock_components = ["script(LLM未接入)", "tts_voice(正弦波)", "lipsync(直通)"]

        # 写指标 JSON
        metrics_path = self.output_dir / f"{timeline_id}_metrics.json"
        metrics_path.write_text(
            json.dumps({**asdict(m), "elapsed_s": round(time.monotonic() - t0, 3),
                        "script_text": text},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log.info("闭环完成: %s, 音画偏差 %sms", out_path, m.av_offset_ms)
        return str(out_path), m
