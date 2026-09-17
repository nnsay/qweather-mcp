# 天文 (Astronomy)

来源: https://dev.qweather.com/docs/api/astronomy/

提供全球任意地点未来 60 天的日出日落、月升月落和月相、太阳高度角数据。

## 日出日落

https://dev.qweather.com/docs/api/astronomy/sunrise-sunset/

```
GET /v7/astronomy/sun?location=116.41,39.92&date=20260101
```

参数：`location`（LocationID 或 `经度,纬度`）、`date`（`yyyyMMdd`，今天起 60 天内）。

响应：`sunrise`、`sunset`（高纬度极昼/极夜时可能为空）。

- 日出：太阳**上边缘**出现在地平线的时刻；日落：太阳**上边缘**完全消失于地平线的时刻。
- API 时间受大气折射、海拔、地形、云雾影响，**≠ 肉眼一定能看见太阳的时间**。

## 月升月落和月相

https://dev.qweather.com/docs/api/astronomy/moon-and-moon-phase/

```
GET /v7/astronomy/moon?location=116.41,39.92&date=20260101
```

参数：`location`（LocationID 或 `经度,纬度`）、`date`（`yyyyMMdd`，今天起 60 天内）。

响应：`moonrise`、`moonset`、`moonPhase[]`：

- `fxTime`：逐小时预报时间
- `value`：月相数值（string）
- `name`：月相名称（中文时如「亏凸月」；亦对应 8 种枚举 `new-moon` / `waxing-crescent` / `first-quarter` / `waxing-gibbous` / `full-moon` / `waning-gibbous` / `last-quarter` / `waning-crescent`）
- `illumination`：月亮照明度，百分比
- `icon`：月相图标代码

月升月落日际变化大（平均每天推迟约 50 分钟）；`moonrise` / `moonset` 可能只有其一（事件跨零点），高纬度地区可能两者皆空。

**主导月相**：当天 24 小时内发生新月/上弦月/满月/下弦月之一则取该瞬时月相，否则取当地时间 12:00 的月相。

**8 种月相**（北半球可见比例 / 平均月升 / 平均月落）：

| 名称 | 枚举 | 可见 | 月升 | 月落 |
| --- | --- | --- | --- | --- |
| 新月（朔月） | `new-moon` | 几乎不可见 | 06:00 | 18:00 |
| 蛾眉月 | `waxing-crescent` | 右侧 1-49% | 09:00 | 21:00 |
| 上弦月 | `first-quarter` | 右侧 50% | 12:00 | 00:00 |
| 盈凸月 | `waxing-gibbous` | 右侧 51-99% | 15:00 | 03:00 |
| 满月（望月） | `full-moon` | 100% | 18:00 | 06:00 |
| 亏凸月 | `waning-gibbous` | 左侧 99-51% | 21:00 | 09:00 |
| 下弦月 | `last-quarter` | 左侧 50% | 00:00 | 12:00 |
| 残月 | `waning-crescent` | 左侧 49-1% | 03:00 | 15:00 |

南半球月相左右倒置。

## 太阳高度角

https://dev.qweather.com/docs/api/astronomy/solar-elevation-angle/

```
GET /v7/astronomy/solar-elevation-angle?location=116.41,39.92&date=20260101&time=1230&tz=0800&alt=43
```

参数（全部必选）：

- `location`：仅支持 `经度,纬度`（不支持 LocationID）
- `date`：`yyyyMMdd`
- `time`：`HHmm`，24 时制
- `tz`：时区，如 `0800` / `-0530`
- `alt`：海拔高度（米）

响应：`solarElevationAngle`（高度角）、`solarAzimuthAngle`（方位角，0 度为正北）、`solarHour`（太阳时 `HHmm`）、`hourAngle`（时角）。

## 参考资料

### 了解太阳数据（sun-guide）

- **太阳正午 / 子夜**：太阳经过观测者子午圈上方（高度最高）/ 下方（高度最低）的时刻，由经度与太阳视运动决定，**不是**固定 12:00 / 24:00。
- **曙暮光（晨昏蒙影）**：太阳位于地平线下时按几何中心高度角分三阶段——民用（0°～-6°）、航海（-6°～-12°）、天文（-12°～-18°）。
  正常顺序：天文晨光 → 航海晨光 → 民用晨光 → 日出 → 太阳正午 → 日落 → 民用暮光 → 航海暮光 → 天文暮光。
  晨光字段表示阶段「开始」，暮光字段表示「结束」。
- 高纬度地区太阳可能不穿越地平线或某高度角，`sunrise` / `sunset` / 各曙暮光字段可能为空。

### 了解月亮数据（moon-guide）

- **月升 / 月落**：月亮上边缘升过 / 沉入地平线的时刻；平均值约在日出/日落期间。
- **月亮上中天 / 下中天**：月亮两次经过观测者子午圈，多数情况下分别对应当天最高 / 最低高度。
- **月相（moonPhase）**：地球上看到的月球亮面形状，周期约 29.5 天（朔望月）；逐小时返回，`value` 为月相数值、`ilumination` 为照明度。月相是相对位置造成，**非地球影子**（仅月食时被地影遮挡）。
