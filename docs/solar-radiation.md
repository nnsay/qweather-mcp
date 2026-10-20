# 太阳辐射 (Solar Radiation)

来源: https://dev.qweather.com/docs/api/solar-radiation/

全球辐射数据，包括 DNI、DHI、GHI 以及相关气象数据，15 分钟间隔，1 公里分辨率。
**无免费额度，请求即计费**——`QWEATHER_ONLY_FREE=true` 时该工具不暴露（见 server.py 的 `PAID_TOOLS`）。

## 太阳辐射预报

https://dev.qweather.com/docs/api/solar-radiation/solar-radiation-forecast/

```
GET /solarradiation/v1/forecast/{latitude}/{longitude}
```

获取全球任意坐标的逐 15 分钟太阳辐射预报及相关数据，最多支持未来 72 小时，分辨率 1×1 公里。

路径参数（经纬度，十进制，最多两位小数）：

- `latitude` 必选，如 `39.92`
- `longitude` 必选，如 `116.41`

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `hours` | integer | 预报小时数 1-72，默认 `24` |
| `interval` | integer | 时间间隔 `15` / `30` / `60` 分钟，默认 `60` |
| `tilt` | integer | 光伏系统倾斜角 0-90；`extra=poa` 时必传 |
| `azimuth` | integer | 光伏系统方位角 0-359，0 = 北；`extra=poa` 时必传 |
| `extra` | string | `weather`（基本天气）/ `poa`（阵列平面辐照，须同时传 `tilt`+`azimuth`），逗号分隔多项 |
| `localTime` | boolean | `false` UTC（默认）/ `true` 本地时间 |

响应示例：

```json
{
  "metadata": {
    "tag": "c4ca4238a0b923820dcc509a6f75849b"
  },
  "forecasts": [
    {
      "forecastTime": "2023-10-15T11:30Z",
      "solarAngle": { "azimuth": 184, "elevation": 40 },
      "dni": { "value": 25.16, "unit": "W/m²" },
      "dhi": { "value": 136.29, "unit": "W/m²" },
      "ghi": { "value": 152.57, "unit": "W/m²" },
      "weather": {
        "temperature": { "value": 18.6, "unit": "°C" },
        "windSpeed": { "value": 2.78, "unit": "m/s" },
        "humidity": 76
      },
      "poa": {
        "global": { "value": 134.39, "unit": "W/m²" },
        "direct": { "value": 9.35, "unit": "W/m²" },
        "diffuse": { "value": 125.04, "unit": "W/m²" },
        "reflected": { "value": 1.52, "unit": "W/m²" }
      }
    }
  ]
}
```

字段说明：

| 字段 | 含义 |
| --- | --- |
| `metadata.tag` | 数据唯一标识 |
| `metadata.attributions` | 数据归因声明，**必须与数据共同显示** |
| `forecasts[].forecastTime` | 预报时间 |
| `forecasts[].solarAngle.azimuth` | 太阳方位角，正北为 0 度 |
| `forecasts[].solarAngle.elevation` | 太阳高度角 |
| `forecasts[].dni` | 法向直接辐照（Direct Normal Irradiance） |
| `forecasts[].dhi` | 散射水平面辐照（Diffuse Horizontal Irradiance） |
| `forecasts[].ghi` | 总水平面辐照（Global Horizontal Irradiance） |
| `forecasts[].weather` | 仅 `extra=weather` 时返回：温度 / 风速 / 相对湿度 |
| `forecasts[].poa` | 仅 `extra=poa` 时返回：阵列平面总/直接/散射/反射辐照 |

辐照度单位 `W/m²`，温度 `°C`，风速 `m/s`，湿度为纯数值（无 unit 字段）。

## 计费

太阳辐射属付费 API，无免费额度，按量计费：https://dev.qweather.com/docs/finance/pricing/
