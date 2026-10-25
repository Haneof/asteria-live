#!/usr/bin/env bash
set -euo pipefail

# 启动脚本：默认在 127.0.0.1:8000 启动管理 API。
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -e ".[dev]"
exec python -m asteria "$@"
