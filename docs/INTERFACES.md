# 接口契约 — INTERFACES.md

> 共享接口与数据契约。修改公共接口前必须经主控 Agent 协调，保持向后兼容或显式升版本。

## 1. 时间轴（ASTERIA-SYNC）

- 单位：整数毫秒（`int`）。
- 区间：`[start_ms, end_ms)`，半开区间。
- 原始媒体 PTS 与 `time_base`（`num/den`）必须保留，不与毫秒时间轴混用。

```python
class MediaTimestamp:
    pts: int            # 原始 PTS
    time_base_num: int
    time_base_den: int
    ms: int             # 换算后的毫秒（内部时间轴）
```

## 2. 模型能力分级

```python
class CapabilityLevel(Enum):
    DOCUMENTED = "documented"
    TESTED = "tested"
    PRODUCTION_VALIDATED = "production_validated"
```

每个适配器必须声明当前等级，禁止将 Mock 冒充真实模型。

## 3. 适配器接口（当前草案）

```python
class TTSAdapter(Protocol):
    level: CapabilityLevel
    def synthesize(self, text: str, timeline_id: str) -> AudioSegment: ...

class LipSyncAdapter(Protocol):
    level: CapabilityLevel
    def drive(self, audio: AudioSegment, video: VideoSegment) -> VideoSegment: ...

class VideoSourceAdapter(Protocol):
    level: CapabilityLevel
    def read(self, asset_id: str, span: TimeSpan) -> VideoSegment: ...

class StreamAdapter(Protocol):
    level: CapabilityLevel
    def push(self, frames: Iterator[VideoSegment]) -> StreamStats: ...
```

## 4. 错误码约定

| 码 | 含义 |
|----|------|
| OK | 成功 |
| ERR_INVALID_ARG | 参数非法 |
| ERR_UNSAFE_PATH | 动作无安全回归路径，拒绝调度 |
| ERR_EXTERNAL | 外部服务失败（超时/限流/熔断） |
| ERR_NOT_IMPLEMENTED | 未实现能力 |

## 5. 版本兼容规则

- 公共接口变更需升版本号（语义化）。
- 破坏性变更需在 DECISIONS.md 记录并通知依赖方。
- 数据库迁移由主控 Agent 统一协调。
