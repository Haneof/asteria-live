"""健康检查与 Mock 适配器测试。"""

from fastapi.testclient import TestClient

from asteria.adapters.mock import MockTTS, MockStream
from asteria.core.types import TimeSpan
from asteria.server.app import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_mock_tts_returns_audio():
    tts = MockTTS()
    seg = tts.synthesize("你好", timeline_id="t1")
    assert seg.timeline_id == "t1"
    assert seg.data is not None


def test_mock_stream_counts_frames():
    stream = MockStream()
    seg = MockTTS().synthesize("x", "t1")
    frames = iter([])
    result = stream.push(frames)
    assert result["pushed_frames"] == 0
    assert result["target"] == "mock"


def test_timespan_used_by_video():
    from asteria.adapters.mock import MockVideoSource
    src = MockVideoSource()
    seg = src.read("asset-1", TimeSpan(0, 2000))
    assert seg.span.duration_ms == 2000
