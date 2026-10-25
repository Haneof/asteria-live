"""配置加载与校验。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    output_width: int = 1280
    output_height: int = 720
    target_fps: float = 25.0
    video_dir: str = "data/videos"
    extra: dict = field(default_factory=dict)


def _load_from_env(cfg: AppConfig) -> None:
    """从环境变量覆盖默认配置（键名映射）。"""
    mapping = {
        "ASTERIA_HOST": "host",
        "ASTERIA_PORT": "port",
        "ASTERIA_LOG_LEVEL": "log_level",
        "ASTERIA_WIDTH": "output_width",
        "ASTERIA_HEIGHT": "output_height",
        "ASTERIA_FPS": "target_fps",
        "ASTERIA_VIDEO_DIR": "video_dir",
    }
    for env_key, attr in mapping.items():
        raw = os.environ.get(env_key)
        if raw is None:
            continue
        if attr in ("port", "output_width", "output_height"):
            setattr(cfg, attr, int(raw))
        elif attr == "target_fps":
            setattr(cfg, attr, float(raw))
        else:
            setattr(cfg, attr, raw)


def load_config() -> AppConfig:
    cfg = AppConfig()
    _load_from_env(cfg)
    cfg.validate()
    return cfg


def validate(cfg: AppConfig) -> None:
    """校验配置合法性，非法即抛错。"""
    if not (0 < cfg.port < 65536):
        raise ValueError(f"非法端口: {cfg.port}")
    if cfg.output_width <= 0 or cfg.output_height <= 0:
        raise ValueError("输出分辨率必须为正")
    if cfg.target_fps <= 0:
        raise ValueError("目标 FPS 必须为正")
    if cfg.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(f"非法日志级别: {cfg.log_level}")


AppConfig.validate = validate  # type: ignore[attr-defined]
