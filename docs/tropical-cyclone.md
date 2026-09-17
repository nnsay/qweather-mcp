# 热带气旋（台风）(Tropical Cyclone)

来源: https://dev.qweather.com/docs/api/tropical-cyclone/

提供全球主要海洋流域的台风实时位置、路径与预报数据。当前中国沿海仅支持西北太平洋流域 `basin=NP`。

三个端点均使用 v7 风格查询参数，与地理位置无关。

## 台风列表

https://dev.qweather.com/docs/api/tropical-cyclone/storm-list/

```
GET /v7/tropical/storm-list?basin=NP&year=2024
```

查询参数：

- `basin` 必选：流域，当前仅支持 `NP`（西北太平洋）。可选值还有 `AL` 北大西洋、`EP` 东太平洋、`SP` 西南太平洋、`NI` 北印度洋、`SI` 南印度洋
- `year` 必选：仅支持本年度和上一年度

响应 `storm[]`：

- `id`：台风 ID
- `name`：台风名称
- `basin`：流域
- `year`：年份
- `isActive`：`1` 活跃台风，`0` 停编

## 台风实况和路径

https://dev.qweather.com/docs/api/tropical-cyclone/storm-track/

```
GET /v7/tropical/storm-track?stormid=NP2018
```

查询参数：`stormid` 必选，台风 ID（来自台风列表）。

响应：

- `isActive`：`1` 活跃台风，`0` 停编
- `now`：当前实况（台风已结束则可为 `null`）
- `track[]`：轨迹数据列表

`now` 与 `track[]` 中的单条数据结构：

- `pubTime`（仅 `now`）/ `time`（`track[]`）：发布时间
- `lat` / `lon`：中心纬度 / 经度
- `type`：台风类型（如 `TD` 热带低压、`TS` 热带风暴、`STS` 强热带风暴、`TY` 台风）
- `pressure`：中心气压 (hPa)
- `windSpeed`：附近最大风速 (m/s)
- `moveSpeed`：移动速度；`moveDir`：移动方位；`move360`：移动方位 360 度
- `windRadius30` / `windRadius50` / `windRadius64`：分别对应 7 级 / 10 级 / 12 级风圈半径，各含 `neRadius` / `seRadius` / `swRadius` / `nwRadius`（可能为空）

## 台风预报

https://dev.qweather.com/docs/api/tropical-cyclone/storm-forecast/

```
GET /v7/tropical/storm-forecast?stormid=NP2018
```

查询参数：`stormid` 必选。查询的台风如果已经结束，返回的 `forecast` 为空，建议先通过台风列表接口确认状态。

响应 `forecast[]`：

- `fxTime`：预报时间
- `lat` / `lon`：预测中心纬度 / 经度
- `type`：台风类型
- `pressure`：中心气压
- `windSpeed`：附近最大风速
- `moveSpeed` / `moveDir` / `move360`：移动速度 / 方位 / 方位 360 度
