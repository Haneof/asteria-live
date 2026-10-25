# Asteria 星枢 — 数字人实时演播与直播平台

以本地动作素材库、多锚点动作图谱、AI 内容编导和音视频同步为核心的低算力数字人系统。

> 动作有图谱，演播有中枢。

## 项目状态

| 阶段 | 状态 |
|------|------|
| G0 仓库与治理 | 进行中 |
| G1 可运行工程骨架 | 未开始 |
| G2 最小实时闭环 | 未开始 |
| G3 素材分析与动作图谱 | 未开始 |
| G4 资产生产与质量治理 | 未开始 |
| G5 商品知识与内容编导 | 未开始 |
| G6 互动与运营复盘 | 未开始 |
| G7 性能与发布 | 未开始 |

## 技术栈（当前实际）

- Python 3.11（应用与媒体编排）
- FastAPI（管理 API）
- FFmpeg（媒体解码/编码/合成；含 h264_nvenc 编码器支持，需 NVIDIA 硬件）
- pytest（测试）
- SQLite（本地原型存储，待评估）

> PyAV 尚未安装；口型/ASR/TTS/视频生成模型均以 Mock 适配器占位，待接入真实模型后更新能力分级。

## 环境要求

- Python 3.11+
- FFmpeg（`ffmpeg`、`ffprobe` 在 PATH）
- 目标部署：NVIDIA GPU PC，约 8GB 显存（非当前开发沙箱）

## 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 启动

```bash
python -m asteria
# 或
./scripts/run.sh
```

## 测试

```bash
pytest -q
```

## 目录结构

```
asteria/           主包
  core/            共享类型、时间轴、状态机
  adapters/        TTS/口型/视频源/推流等适配器（含 Mock）
  graph/           动作图谱（多锚点有向图）
  server/          FastAPI 管理 API
docs/              治理与契约文档
tests/             测试
scripts/           启动/辅助脚本
```

详细架构见 `docs/ARCHITECTURE.md`，接口契约见 `docs/INTERFACES.md`。
