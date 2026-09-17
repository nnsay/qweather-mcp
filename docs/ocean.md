# 海洋数据 (Ocean)

来源: https://dev.qweather.com/docs/api/ocean/

提供全球主要港口和城市的潮汐数据。

## 潮汐

https://dev.qweather.com/docs/api/ocean/tide/

```
GET /v7/ocean/tide?location=P66981&date=20260101
```

查询参数：

- `location` 必选：潮汐观测站的 LocationID，例如 `P66981`。潮汐站可通过 GeoAPI 的 POI 搜索（`type=TSTA`）按港口/城市获取
- `date` 必选：日期 `yyyyMMdd`，最多可选择未来 10 天（含今天）

响应：

- `tideTable[]`：满潮/干潮表
  - `fxTime`：预报时间
  - `height`：海水高度，单位米
  - `type`：满潮 `H` 或干潮 `L`
- `tideHourly[]`：逐小时潮位
  - `fxTime`：预报时间
  - `height`：海水高度，单位米
