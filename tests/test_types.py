"""时间轴类型单元测试。"""

import pytest

from asteria.core.types import CapabilityLevel, MediaTimestamp, TimeSpan


def test_timespan_valid():
    ts = TimeSpan(start_ms=0, end_ms=1000)
    assert ts.duration_ms == 1000
    assert ts.contains(0)
    assert ts.contains(999)
    assert not ts.contains(1000)


def test_timespan_rejects_invalid():
    with pytest.raises(ValueError):
        TimeSpan(start_ms=1000, end_ms=500)
    with pytest.raises(ValueError):
        TimeSpan(start_ms=-1, end_ms=10)


def test_capability_level_distinct():
    levels = {CapabilityLevel.DOCUMENTED, CapabilityLevel.TESTED,
              CapabilityLevel.PRODUCTION_VALIDATED}
    assert len(levels) == 3


def test_media_timestamp_keeps_pts():
    mt = MediaTimestamp(pts=90000, time_base_num=1, time_base_den=90000, ms=1000)
    assert mt.pts == 90000
    assert mt.ms == 1000
