# 项目基线 — PROJECT_BASELINE.md

> 本文件记录真实环境与产品约束，事实按「已证实 / 部分证实 / 尚未实现 / 无法验证」分级。

## 1. 环境基线（第一轮实测，2026-10-25）

| 项目 | 值 | 状态 |
|------|-----|------|
| 操作系统 | Ubuntu 24.04.3 LTS | 已证实 |
| Python | 3.11.1（pyenv） | 已证实 |
| Node.js | v22.13.1 | 已证实 |
| pip | 26.0.1 | 已证实 |
| git | 2.43.0 | 已证实 |
| FFmpeg | N-124111-g9e90fa505e（含 h264_nvenc/hevc_nvenc/av1_nvenc/aac 编码器） | 已证实 |
| pytest | 9.0.2 | 已证实 |
| FastAPI | 0.128.2 | 已证实 |
| numpy | 2.3.5 | 已证实 |
| PyAV（av） | 未安装 | 尚未实现 |
| NVIDIA GPU | `nvidia-smi` 不存在 | 无法验证（当前沙箱无 GPU） |
| 磁盘 | overlay 256G，可用 254G | 已证实 |
| 仓库 | /workspace 初始为空，已 `git init -b main` | 已证实 |

## 2. 产品目标（目标值，未经实测不得宣称达标）

| 项目 | 目标 |
|------|------|
| 硬件 | NVIDIA GPU PC，约 8GB 显存 |
| 输出 | 720p、25 FPS |
| 连续运行 | 单场 4–5 小时 |
| 主链路 | 本地预制动作视频库；远程生成仅可选补充 |
| 音频 | TTS 产出最终音频，口型由实际播放音频驱动 |

## 3. 架构模块（逻辑划分）

- ASTERIA-FORGE：素材导入、ASR、姿态数据化、动作分段、锚点候选、资产生产与质量验证。
- ASTERIA-DIRECTOR：商品知识、话术模板、脚本时间线、动作语义映射、互动决策、复盘。
- ASTERIA-LIVE：状态机调度、TTS、口型、媒体合成、推流、监控、人工接管。
- 公共：ASTERIA-GRAPH、ASTERIA-SYNC、ASTERIA-ASSETS、ASTERIA-OBSERVE。

## 4. 模型选型状态（均为候选，未验证）

| 候选 | 状态 |
|------|------|
| Wav2Lip | 未接入，未验证 |
| MuseTalk | 未接入，未验证 |
| FFmpeg/PyAV | FFmpeg 已证实；PyAV 未安装 |
| ASR 模型 | 未选型 |
| NVENC | 编码器存在，但无 GPU 硬件无法实测 |
| Vidu S2 | 未接入，未验证 |

## 5. 关键工程契约

- 内部时间轴整数毫秒，保留原始 PTS/time_base；区间 `[start_ms, end_ms)`。
- 模型能力分级：DOCUMENTED / TESTED / PRODUCTION_VALIDATED，不得混淆。
- 音画同步基于时间戳与缓冲策略，禁止固定 sleep。
- 动作图谱多锚点有向图；正式可调度动作必须有经过验证的安全回归路径。
- 外部调用必须有超时、错误分类、重试上限、熔断/降级与脱敏日志。
