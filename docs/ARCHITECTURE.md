# 架构 — ARCHITECTURE.md

> 本文档描述实际架构。MVP 阶段采用单机、可测试的工程结构，不强制微服务。

## 1. 逻辑模块与职责

```
ASTERIA-FORGE      素材导入 → ASR → 姿态数据化 → 动作分段 → 锚点候选 → 资产生产与质量验证
ASTERIA-DIRECTOR   商品知识 → 话术模板 → 脚本时间线 → 动作语义映射 → 互动决策 → 复盘
ASTERIA-LIVE       状态机调度 → TTS → 口型 → 媒体合成 → 推流 → 监控 → 人工接管
```

公共能力：
- ASTERIA-GRAPH：多锚点有向动作图谱。
- ASTERIA-SYNC：时间戳对齐与缓冲策略。
- ASTERIA-ASSETS：资产存储与版本管理。
- ASTERIA-OBSERVE：结构化日志、指标与监控。

## 2. 当前工程结构（实际）

```
asteria/
  core/       共享类型（时间轴等）、配置、日志
  adapters/   TTS / 口型 / 视频源 / 推流 适配器（含 Mock）
  graph/      动作图谱
  server/     FastAPI 管理 API
tests/
scripts/
docs/
```

## 3. 依赖方向

- `core` 不依赖任何上层模块。
- `adapters`、`graph` 依赖 `core`。
- `server` 依赖 `adapters`、`graph`、`core`。
- 实时主链路不得强依赖远程生成服务。

## 4. 时间基准

- 内部统一整数毫秒，保留原始 PTS/time_base。
- 区间 `[start_ms, end_ms)`。
- 视频、音频、ASR、姿态、动作、脚本事件经 `timeline_id` 对齐。

## 5. 技术选型（已证实部分）

| 组件 | 选型 | 状态 |
|------|------|------|
| 应用框架 | Python 3.11 + FastAPI | 已证实可用 |
| 媒体处理 | FFmpeg（PyAV 待装） | FFmpeg 已证实 |
| 存储 | SQLite（原型） | 待接入 |
| 测试 | pytest | 已证实 |
| 模型 | Mock 适配器占位 | 未接入真实模型 |
