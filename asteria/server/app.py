"""FastAPI 管理 API 与健康检查。"""

from __future__ import annotations

from fastapi import FastAPI

from asteria import __version__
from asteria.core.config import AppConfig

app = FastAPI(title="Asteria 星枢", version=__version__)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


def create_app(cfg: AppConfig | None = None) -> FastAPI:
    # cfg 参数预留用于后续注入，当前仅返回默认 app。
    return app
