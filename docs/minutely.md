# 分钟预报 (Minutely)

来源: https://dev.qweather.com/docs/api/minutely/

分钟级降水（临近预报）：中国 1 公里精度，未来 2 小时每 5 分钟降水预报，数据每 5 分钟更新。仅中国区域。

## 分钟级降水

https://dev.qweather.com/docs/api/minutely/minutely-precipitation/

```
GET /v7/minutely/5m?location={经度,纬度}
```

`location`：以英文逗号分隔的 `经度,纬度`（十进制，最多两位小数），如 `116.41,39.92`。仅接受坐标，不接受城市名 / LocationID。

响应：

- `summary`：一句话降水描述，如「95分钟后雨就停了」
- `minutely[]`：每 5 分钟一条
  - `fxTime`：预报时间
  - `precip`：5 分钟累计降水量（毫米）
  - `type`：`rain` 雨 / `snow` 雪
