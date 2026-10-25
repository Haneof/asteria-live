"""配置校验测试。"""

import pytest

from asteria.core.config import AppConfig, load_config


def test_default_config_valid():
    cfg = AppConfig()
    cfg.validate()  # 不应抛错


def test_load_config_defaults():
    cfg = load_config()
    assert cfg.port == 8000
    assert cfg.output_width == 1280
    assert cfg.output_height == 720


def test_config_rejects_bad_port():
    cfg = AppConfig(port=0)
    with pytest.raises(ValueError):
        cfg.validate()


def test_config_rejects_bad_fps():
    cfg = AppConfig(target_fps=0)
    with pytest.raises(ValueError):
        cfg.validate()
