# Asteria 星枢 — 开发者指南（DEVELOPMENT）

> 本文件面向**接手本项目开发的工程师**。它描述当前仓库的**真实状态**：已实现的代码、模块边界、如何运行与测试、如何扩展，以及必须遵守的研发纪律。
> 凡涉及"能力等级 / 是否真实跑通"，一律以仓库内代码与 `docs/MASTER_TASKS.md` 账本为准，不提前宣称达标。
> 全局规则见根目录 `AGENTS.md`，架构、接口、验收、风险、决策分别见 `docs/` 下对应文件。

---

## 1. 项目定位与目标基线

Asteria 星枢是一个以**本地动作素材库 + 多锚点动作图谱 + AI 内容编导 + 音视频同步**为核心的**低算力数字人实时演播系统**。

| 目标项 | 取值 | 当前状态 |
|--------|------|----------|
| 目标硬件 | NVIDIA GPU PC，约 8GB 显存 | 目标值，开发沙箱**无 GPU** |
| 目标输出 | 720p、25 FPS | 目标值，尚未在目标硬件实测 |
| 连续运行 | 单场 4–5 小时 | 目标值，未实测 |
| 实时主链路 | 本地预制动作视频库 | 已建最小闭环（G2） |
| 远程视频生成 | 可选补充（如 Vidu S2） | 不得成为实时主链路强依赖 |

口号：**动作有图谱，演播有中枢。**

---

## 2. 当前真实进度（截至 2026-10-26）

阶段划分 G0–G7。以 `docs/MASTER_TASKS.md` 账本状态为准；下表标注"代码实际"一列，用于暴露账本与代码可能的不一致，便于接手后先对齐账本。

| 阶段 | 账本状态 | 代码实际 | 说明 |
|------|----------|----------|------|
| G0 仓库与治理 | IN_PROGRESS | 已完成 | 治理文件、`AGENTS.md`、`docs/*` 已建 |
| G1 工程骨架 | TODO | **已完成未标 PASS** | `asteria` 包、配置、日志、健康检查、类型、Mock 适配器、测试全在 |
| G2 最小闭环 | PASS | PASS | 真实读视频→合成→指标；话术/TTS/口型为 Mock |
| G3 动作图谱 | TODO | 未开始 | `graph/` 目录尚不存在 |
| G4 资产生产 | TODO | 未开始 | — |
| G5 商品编导 | TODO | 未开始 | — |
| G6 互动复盘 | TODO | 未开始 | — |
| G7 性能发布 | TODO | 未开始 | — |

> **接手第一步建议**：先按代码真实情况把 G1-001 账本状态更新为 PASS 并补证据，消除账本滞后。

### 真实 vs Mock 边界（G2 闭环实测）

`asteria/pipeline/loop.py::LiveLoop` 已跑通，各组件边界如下：

| 组件 | 实现 | 是否真实 | 说明 |
|------|------|----------|------|
| 视频读取 | `FFMpegVideoSource` + ffprobe | ✅ 真实 | 元数据来自真实 ffprobe 探测 |
| 话术生成 | `MockScript` | ❌ Mock | LLM 未接入，模板占位 |
| TTS 音频 | `MockTTSWav` | ⚠️ 半真实 | 生成**合法 WAV 字节流**（正弦波），语音内容非真实 |
| 口型驱动 | `MockLipSync` | ❌ Mock | 直通，未接真实口型模型 |
| 音视频合成 | FFmpeg h264+aac mux | ✅ 真实 | 编码器按可用性选择 |
| 指标测量 | ffprobe 实测输出 | ✅ 真实 | 音画时长偏差等 |

> 任何新接入的模型都必须通过**适配器**接入，并如实标注 `is_mock` 与 `CapabilityLevel`，禁止把 Mock 伪装成真实能力。

---

## 3. 环境搭建

### 3.1 软件依赖

- **Python 3.11+**（项目 `requires-python = ">=3.11"`）
- **FFmpeg**，且 `ffmpeg`、`ffprobe` 在 `PATH` 中，**必须支持 H.264 软编码器之一**

### 3.2 FFmpeg 编码器注意事项（关键坑）

代码 `asteria/pipeline/loop.py::_pick_h264_encoder()` 按可用性选择编码器：

```python
for name in ("libx264", "libopenh264"):
    if f" {name} " in out:
        return name
```

- 优先 `libx264`；不存在则回落 `libopenh264`（软件编码，无需 GPU）。
- 当前**开发沙箱无 GPU**，`h264_nvenc` 不可用，统一走 openh264。
- 你本地若是普通电脑，多数发行版自带 `libx264`；若没有，需安装带 openh264 的 ffmpeg（或自行编译）。
- 验证本地可用编码器：`ffmpeg -hide_banner -encoders | grep -E "libx264|libopenh264"`

### 3.3 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"      # 含 pytest / httpx 等开发依赖
```

`pyproject.toml` 运行时依赖仅 `fastapi`、`uvicorn`；媒体处理走系统 FFmpeg，不依赖 PyAV。

---

## 4. 启动与管理 API

### 4.1 启动服务

```bash
python -m asteria
# 等价于 ./scripts/run.sh
```

入口 `asteria/__main__.py`：加载 `AppConfig` → `setup_logging` → `uvicorn.run("asteria.server.app:app", ...)`。
默认监听 `127.0.0.1:8000`（可用环境变量覆盖，见第 9 节）。

### 4.2 健康检查

```bash
curl http://127.0.0.1:8000/health
# => {"status":"ok","version":"0.1.0"}
```

`asteria/server/app.py` 目前仅暴露 `/health`，`create_app(cfg)` 预留配置注入位。

---

## 5. 运行 G2 最小闭环（验证你环境能跑通）

```bash
python scripts/run_g2_loop.py \
  --video data/raw/merchant_clips/clip_1999_anchor_face_product.mp4 \
  --topic "测试商品" \
  --timeline g2-run
```

**参数**

| 参数 | 必填 | 说明 |
|------|------|------|
| `--video` | 是 | 本地动作视频路径 |
| `--topic` | 否 | 话术主题（默认"测试商品"） |
| `--timeline` | 否 | timeline_id（默认 `g2-run`） |

**输出**：`data/output/{timeline}.mp4` + `{timeline}_audio.wav` + `{timeline}_metrics.json`，并打印指标 JSON（视频/音频/输出时长、音画偏差、分辨率、真实与 Mock 组件清单）。

> G2 实测证据（账本记录）：720p 输入，输出约 2720ms，音画偏差 0ms。注意音画偏差为"输出时长 vs 较短输入时长"的差值，并非逐帧对齐精度——逐帧对齐属后续能力。

---

## 6. 目录结构与模块职责（真实）

```
asteria/
  __main__.py          入口：加载配置→日志→起 uvicorn
  core/
    types.py           TimeSpan / MediaTimestamp / AudioSegment / VideoSegment / CapabilityLevel
    config.py          AppConfig + 环境变量覆盖 + 校验
    logging.py         JSON 行结构化日志（setup_logging / get_logger）
  adapters/
    base.py            适配器基类（约定 is_mock / level 等标记）
    ffmpeg_source.py   真实视频源（FFMpegVideoSource，ffprobe 探测，TESTED）
    mock.py            MockTTS / MockLipSync / MockVideoSource / MockStream
    mock_tts_wav.py    MockTTSWav（生成合法正弦波 WAV，半真实）
  pipeline/
    loop.py            LiveLoop：最小实时闭环编排
  server/
    app.py             FastAPI 应用 + /health
scripts/
  run.sh               启动脚本
  run_g2_loop.py       G2 闭环命令行入口
  record_douyin.py     抖音直播录制（API 版，依赖 /opt/DouyinLiveRecorder）
  watch_douyin_browser.sh  抖音直播监控（浏览器版，依赖 playwright-cli）
tests/                 test_types / test_config / test_app / test_g2_loop（共 15 例）
docs/                  AGENTS / PROJECT_BASELINE / MASTER_TASKS / ARCHITECTURE /
                       INTERFACES / ACCEPTANCE / RISKS / DECISIONS / 本文件
data/                 （gitignore）素材与产物，分 raw/ 与 output/
```

> 注意：`README.md` 目录结构里写的 `graph/` 尚不存在（G3 未开始），以本文件为准。

---

## 7. 核心概念与数据模型

### 7.1 统一时间轴（ASTERIA-SYNC）

- 内部时间轴用**整数毫秒**；区间统一为**半开区间** `[start_ms, end_ms)`。
- 原始媒体 `PTS` 与 `time_base` **必须保留**（`MediaTimestamp`），不得与毫秒轴混用。
- 视频、音频、ASR、姿态、动作事件、脚本事件通过 `timeline_id` 对齐。
- **禁止**依赖固定 `sleep` 保证音画同步，必须用时间戳、缓冲策略和实测指标。

### 7.2 关键类型（`asteria/core/types.py`）

| 类型 | 作用 |
|------|------|
| `TimeSpan(start_ms, end_ms)` | 半开区间，带 `duration_ms` / `contains(ms)`；构造即校验合法性 |
| `MediaTimestamp(pts, time_base_num, time_base_den, ms)` | 保留原始 PTS 与 time_base |
| `AudioSegment(timeline_id, span, sample_rate, data?, path?)` | 音频段引用（字节或文件） |
| `VideoSegment(timeline_id, span, fps, width, height, path?, frames?)` | 视频段引用 |
| `CapabilityLevel` | `DOCUMENTED` / `TESTED` / `PRODUCTION_VALIDATED`（三级，禁止混淆） |

### 7.3 能力分级（重要）

所有模型/外部能力必须标级，且**三级不得混淆**：

- `DOCUMENTED`：有官方文档依据（尚未在本环境跑测）
- `TESTED`：已在指定环境完成可复现测试
- `PRODUCTION_VALIDATED`：已在目标运行条件完成生产级验证

当前：视频源 `FFMpegVideoSource.level = TESTED`；其余 Mock 适配器均为 `DOCUMENTED`（且 `is_mock=True`）。

---

## 8. 适配器模式与真实/Mock 边界

所有外部能力（TTS、口型、视频源、推流、姿态、ASR、远程生成）都通过**适配器**接入。约定：

- 适配器类标注 `is_mock: bool` 与 `level: CapabilityLevel`。
- 真实实现必须保留超时、错误分类、重试上限、可观测日志（见 `AGENTS.md` §7）。
- 远程生成失败**不得拖垮**本地实时主链路（降级到本地素材库）。

**如何新增一个真实适配器（以 TTS 为例）**

1. 在 `asteria/adapters/` 新建 `real_tts.py`，实现与 `MockTTS`/`MockTTSWav` 一致的接口（`synthesize(text, timeline_id) -> AudioSegment`）。
2. 标注 `is_mock = False`、`level = CapabilityLevel.TESTED`（跑通测试后）。
3. 加入超时与日志；异常分类后抛出，不让调用方无感知。
4. 在 `LiveLoop` 中替换 `self.tts` 为真实适配器，并同步更新 G2-001 账本的真实/Mock 组件清单与证据。

> 接口契约细节见 `docs/INTERFACES.md`；架构边界见 `docs/ARCHITECTURE.md`。

---

## 9. 配置

`asteria/core/config.py::AppConfig` 默认值：

| 字段 | 默认 | 环境变量覆盖 |
|------|------|--------------|
| `host` | 127.0.0.1 | `ASTERIA_HOST` |
| `port` | 8000 | `ASTERIA_PORT` |
| `log_level` | INFO | `ASTERIA_LOG_LEVEL` |
| `output_width` | 1280 | `ASTERIA_WIDTH` |
| `output_height` | 720 | `ASTERIA_HEIGHT` |
| `target_fps` | 25.0 | `ASTERIA_FPS` |
| `video_dir` | data/videos | `ASTERIA_VIDEO_DIR` |

`load_config()` 会做合法性校验（`validate()`）：端口、分辨率、FPS、日志级别非法即抛错。

---

## 10. 测试

```bash
pytest -q                 # 全量，15 例
pytest tests/test_g2_loop.py -q   # 仅 G2 闭环（含 ffprobe 真实元数据、WAV 流、全链路）
```

覆盖范围：

- `test_types.py`：时间轴/区间/类型约束
- `test_config.py`：配置加载与校验
- `test_app.py`：`/health` 返回 200
- `test_g2_loop.py`：3 项 G2 端到端（真实 ffprobe 元数据、真实 WAV 流校验、全链路闭环）

> 测试命令与断言必须反映**真实**行为。例如 G2 输出时长跟随音频（`-shortest`），断言应针对音频真实时长，而非输入视频名义时长。

---

## 11. 如何扩展：接入真实能力路线图

| 待接能力 | 对应任务 | 入口/落点 | 备注 |
|----------|----------|-----------|------|
| 真实 TTS 语音 | R1 选型 | `adapters/real_tts.py` 替换 `LiveLoop.tts` | 产出最终播放音频 |
| 真实口型 | — | 替换 `MockLipSync` | **必须以实际播放音频为输入** |
| 姿态估计 | G3-002 | 新建 `adapters/pose.py` | 输出骨骼张量 `R^{T×N×C}`，保留坐标系/置信度/schema 版本 |
| 动作图谱 | G3-001 | 新建 `graph/` | 多锚点有向图、安全回归路径 |
| ASR 话术 | G3-003 | 新建 `adapters/asr.py` | 与姿态对齐，构建三元组 |
| LLM 话术/编导 | G5-001 | 替换 `MockScript` | 只做高层话术/动作意图，不逐帧控媒体 |

**架构分层（逻辑模块）**：ASTERIA-FORGE（素材/ASR/姿态/资产）、ASTERIA-DIRECTOR（商品/话术/脚本/动作语义）、ASTERIA-LIVE（状态机/TTS/口型/合成/推流/监控）。公共能力：ASTERIA-GRAPH、ASTERIA-SYNC、ASTERIA-ASSETS、ASTERIA-OBSERVE。MVP 阶段优先简单可测结构，不强制微服务。

---

## 12. 动作图谱规则（G3 设计约束，提前记牢）

- 采用**多锚点有向图谱**，而非单一固定首尾帧循环。
- 支持主基础锚点 A0、局部锚点、主干、旁路、交叉边、局部闭环、转换/恢复动作。
- 不是所有动作都必须首尾帧相同，但每个**正式可调度动作**必须有经测试的安全退出/回归路径。
- **没有验证过的安全路径，禁止发布到正式调度库**；无法规划时进入安全待机或拒绝执行，不得随机选不兼容动作。
- 路径搜索需考虑：锚点兼容性、动作意图、时长、视觉突变风险、重复惩罚、资产状态、回归可达性。

详见 `docs/ARCHITECTURE.md` §5 与 `docs/RISKS.md`。

---

## 13. 开发纪律与红线（摘要，完整见 AGENTS.md）

1. **Git 是唯一事实源**：代码、配置、测试、契约、账本、决策、验收均可追溯；聊天/口头不算。
2. **先读再改**：动代码前先读 `AGENTS.md` 与关联契约，检查真实仓库/环境，不假设路径与状态。
3. **不伪造**：未实现/未运行/未验证的事项如实标记；禁止编造测试结果、模型能力、性能数据、提交记录。
4. **最小必要变更 + 可重复测试**：小而明确的提交；合并前查 diff、测试、接口兼容、密钥泄漏、回归。
5. **素材与密钥不入库**：`data/`、`.env`、token、密码、真实平台凭据**不得提交**；`.gitignore` 已覆盖 `data/`、`logs/`、`*.mp4`、`*.wav` 等。
6. **能力分级不乱用**：`DOCUMENTED/TESTED/PRODUCTION_VALIDATED` 三级不可混淆。
7. **商品与平台事实约束**：价格/库存/SKU/功效等须有可追溯来源；过期/缺失时阻断确定性陈述或转人工；弹幕/挂载/推流须核实真实授权，无权限则降级，不得伪造成功。
8. **任务治理**：所有任务进 `docs/MASTER_TASKS.md`，唯一 ID，状态仅限 TODO/IN_PROGRESS/BLOCKED/REVIEW/PASS/FAIL；只有实际实现+验收证据才可标 PASS。

---

## 14. 常见问题

**Q1：`ffmpeg` 报找不到编码器 / 合成失败？**
A：检查 `ffmpeg -hide_banner -encoders | grep -E "libx264|libopenh264"`，确保至少一个 H.264 软编码器可用；无 GPU 时走 openh264。

**Q2：跑 G2 没有素材 / `data/` 不存在？**
A：`data/` 被 `.gitignore` 忽略，不会随仓库分发。需自行放入视频到 `data/raw/`，或用项目方提供的 `asteria-live-data.tar.gz` 素材包解压。可用公开 CC 测试片（如 Blender 基金会 Sintel / Big Buck Bunny）。

**Q3：`pytest` 报错"No module named asteria"？**
A：未安装包。先 `pip install -e ".[dev]"`（editable 安装）。

**Q4：口型/话术是真实的吗？**
A：否。当前 G2 中话术（`MockScript`）、口型（`MockLipSync`）为 Mock，TTS 为正弦波 WAV（半真实）。真实模型尚未接入，见第 11 节路线图。

**Q5：能直接 `git clone` 拿到全部吗？**
A：源码可 `git clone git@github.com:Haneof/asteria-live.git`；但素材（`data/`）不入库，需单独获取（见 Q2）。

---

## 15. 一句话上手清单

```bash
git clone git@github.com:Haneof/asteria-live.git
cd asteria-live
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
# 放入素材到 data/raw/ 后：
pytest -q
python -m asteria                      # 起服务，/health 自检
python scripts/run_g2_loop.py --video data/raw/<你的视频>.mp4 --topic "测试商品"
```
