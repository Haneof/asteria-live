"""G2 闭环测试：真实 FFprobe/FFmpeg + Mock TTS/口型。"""

import subprocess
from pathlib import Path

import pytest

from asteria.adapters.ffmpeg_source import FFMpegVideoSource
from asteria.adapters.mock_tts_wav import MockTTSWav
from asteria.pipeline.loop import LiveLoop

FFMPEG_ASSETS = Path(__file__).parent.parent / "data" / "raw"
SAMPLE = FFMPEG_ASSETS / "Big_Buck_Bunny_720_10s_1MB.mp4"


@pytest.fixture(scope="module")
def sample_video() -> str:
    if not SAMPLE.exists():
        pytest.skip("测试素材未下载，先运行 scripts/fetch_assets.sh")
    return str(SAMPLE)


def test_ffprobe_real_metadata(sample_video):
    src = FFMpegVideoSource()
    seg = src.read(sample_video)
    assert seg.width == 1280 and seg.height == 720
    assert 9000 <= seg.span.duration_ms <= 11000
    assert 20 <= seg.fps <= 35
    assert seg.path == sample_video
    assert src.is_mock is False


def test_mock_tts_real_wav_stream():
    tts = MockTTSWav()
    audio = tts.synthesize("你好直播间", "t1")
    assert audio.data is not None
    # 校验是真实合法 WAV：用 ffprobe 读流信息
    p = Path("/tmp/g2_tts_check.wav")
    p.write_bytes(audio.data)
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_name,sample_rate,channels", "-of", "csv=p=0", str(p)]
    ).decode().strip()
    codec, rate, ch = out.split(",")
    assert codec == "pcm_s16le" and rate == "24000" and ch == "1"
    assert audio.span.duration_ms >= 500


def test_full_loop_end_to_end(sample_video, tmp_path):
    loop = LiveLoop(output_dir=str(tmp_path))
    out_path, m = loop.run(sample_video, "测试商品", "g2-test")

    out = Path(out_path)
    assert out.exists() and out.stat().st_size > 0

    # 真实指标断言
    assert m.width == 1280 and m.height == 720
    # 输出跟随话术音频时长（-shortest 语义）：音频 < 视频时，输出=音频时长
    assert m.audio_duration_ms < m.video_duration_ms
    assert abs(m.output_duration_ms - m.audio_duration_ms) <= 300, \
        f"音画偏差过大: {m.av_offset_ms}ms"
    assert m.av_offset_ms <= 300

    # Mock 边界必须如实记录
    assert "lipsync(直通)" in m.mock_components
    assert "ffmpeg_mux" in m.real_components

    # 输出必须是合法 mp4（ffprobe 可读，含音频流）
    probe = subprocess.check_output(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_streams", out_path]
    ).decode()
    assert '"codec_type": "audio"' in probe
    assert '"codec_type": "video"' in probe

    # 指标 JSON 已落盘
    metrics = Path(loop.output_dir) / "g2-test_metrics.json"
    assert metrics.exists()
