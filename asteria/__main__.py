"""应用入口。"""

from __future__ import annotations

import uvicorn

from asteria.core.config import load_config
from asteria.core.logging import setup_logging


def main() -> None:
    cfg = load_config()
    setup_logging(cfg.log_level)
    uvicorn.run(
        "asteria.server.app:app",
        host=cfg.host,
        port=cfg.port,
        log_level=cfg.log_level.lower(),
    )


if __name__ == "__main__":
    main()
