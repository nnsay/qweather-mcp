# 空气质量 (Air Quality)

来源: https://dev.qweather.com/docs/api/air-quality/

1 公里分辨率，覆盖全球 100+ 国家和地区，支持各国本地空气质量标准 + 和风通用 AQI。所有端点均为经纬度路径参数（十进制，最多两位小数），无需 `location` 查询参数。

三个端点返回结构一致：`indexes[]`（AQI 指数）与 `pollutants[]`（污染物浓度与分指数）。

## 实时空气质量

https://dev.qweather.com/docs/api/air-quality/air-current/

```
GET /airquality/v1/current/{latitude}/{longitude}
```

响应：`indexes[]`、`pollutants[]`、`stations[]`。

## 空气质量小时预报

https://dev.qweather.com/docs/api/air-quality/air-hourly-forecast/

```
GET /airquality/v1/hourly/{latitude}/{longitude}
```

响应 `hours[]`（未来 24 小时）：`forecastTime`、`indexes[]`、`pollutants[]`。

## 空气质量每日预报

https://dev.qweather.com/docs/api/air-quality/air-daily-forecast/

```
GET /airquality/v1/daily/{latitude}/{longitude}
```

响应 `days[]`（未来 3 天）：`forecastStartTime`、`forecastEndTime`、`indexes[]`、`pollutants[]`。

## 字段说明

`indexes[]`（AQI）：

- `code`：AQI 代码，见下
- `name`：名称，如 `QAQI` / `AQI (US)`
- `aqi`：数值；`aqiDisplay`：展示值（可能含非数字字符）
- `level`：等级；`category`：类别描述
- `color{red,green,blue,alpha}`：RGBA 颜色
- `primaryPollutant{code,name,fullName}`：首要污染物
- `health{effect, advice{generalPopulation, sensitivePopulation}}`：健康影响与建议

`pollutants[]`：`code`、`name`、`fullName`、`concentration{value,unit}`、
`subIndexes[]{code,aqi,aqiDisplay}`（各 AQI 下的分指数；最差分指数决定首要污染物，`AQI = max(分指数)`）。

## 支持的 AQI（aqi-list）

https://dev.qweather.com/docs/api/air-quality/aqi-list/

最多返回两个 AQI：**通用 AQI（`qaqi`）** + **本地 AQI**。`qaqi` 基于 WHO 2021 指南，支持全球任意地点，**暂不适用于中国**。

| code | 名称 | 地区 | 分段 |
| --- | --- | --- | --- |
| `qaqi` | QAQI | 和风 / WHO 2021 | 0-2 优 / 2.1-4 良 / 4.1-5 中等 / 5.1-7 差 / 7.1-9 很差 / 9.1-10 极差 |
| `cn-mee` | AQI (CN) | 中国 | 0-50 优 / 51-100 良 / 101-150 轻度 / 151-200 中度 / 201-300 重度 / 301-500 严重 |
| `cn-mee-1h` | AQI-1H (CN) | 中国 | 同 `cn-mee` |
| `us-epa` | AQI (US) | 美国 | 0-50 好 / 51-100 中等 / 101-150 敏感人群不健康 / 151-200 不健康 / 201-300 非常不健康 / 301-500 危险 |
| `us-epa-nc` | AQI NowCast (US) | 美国 | 同 `us-epa` |
| `gb-defra` | DAQI (GB) | 英国 | 1-3 低 / 4-6 中 / 7-9 高 / 10 严重 |
| `eu-eea` | EAQI (EU) | 欧盟 | 1 优 / 2 良 / 3 中 / 4 差 / 5 很差 / 6 极差 |
| `fr-atmo` | Indice ATMO (FR) | 法国 | 1 好 / 2 一般 / 3 不好 / 4 差 / 5 很差 / 6 极差 |
| `ca-eccc` | AQHI (CA) | 加拿大 | 1-3 低 / 4-6 中 / 7-10 高 / 10+ 极高 |
| `hk-epd` | AQHI (HK) | 中国香港 | 1-3 低 / 4-6 中 / 7 高 / 8-10 甚高 / 10+ 严重 |
| `mo-smg` | AQI (MO) | 中国澳门 | 0-50 良好 / 51-100 普通 / 101-200 不良 / 201-300 非常不良 / 301-400 严重 / 401-500 有害 |
| `tw-me` | Daily AQI (TW) | 中国台湾省 | 0-50 良好 / 51-100 普通 / 101-150 敏感人群不健康 / 151-200 不健康 / 201-300 非常不健康 / 301-500 危害 |
| `tw-me-1h` | Real-time AQI (TW) | 中国台湾省 | 同 `tw-me` |
| `jp-moe` | AQI (JP) | 日本 | 1 蓝色 / 2 青色 / 3 绿色 / 4 注意 / 5 警报 / 6 严重警报 |
| `kr-moe` | CAI (KR) | 韩国 | 0-50 好 / 51-100 中等 / 101-250 不健康 / 251-500 非常不健康 |
| `sg-nea` | PSI 24H (SG) | 新加坡 | 0-50 良好 / 51-100 适中 / 101-200 不健康 / 201-300 非常不健康 / 301-500 危险 |
| `sg-nea-pm1h` | 1-Hour PM2.5 (SG) | 新加坡 | 0-55 正常 / 56-150 偏高 / 151-250 高 / 251+ 非常高（仅 pm2p5） |
| `th-pcd` | AQI (TH) | 泰国 | 0-25 优秀 / 26-50 良好 / 51-100 中等 / 101-200 不健康 / 201+ 非常不健康 |

## 污染物列表（pollutant-list）

https://dev.qweather.com/docs/api/air-quality/pollutant-list/

| code | 名称 | 全称 | 单位 |
| --- | --- | --- | --- |
| `pm10` | PM 10 | 颗粒物（≤10µm） | μg/m³ |
| `pm2p5` | PM 2.5 | 颗粒物（≤2.5µm） | μg/m³ |
| `co` | CO | 一氧化碳 | mg/m³, μg/m³, ppm |
| `no` | NO | 一氧化氮 | ppm |
| `no2` | NO2 | 二氧化氮 | μg/m³, ppb, ppm |
| `so2` | SO2 | 二氧化硫 | μg/m³, ppb, ppm |
| `o3` | O3 | 臭氧 | μg/m³, ppb, ppm |
| `nmhc` | NMHC | 非甲烷总烃 | ppmC |

**首要污染物**：浓度最高或分指数最差的污染物，代表当前空气污染主要成分。

## 覆盖范围（aqi-coverage）

https://dev.qweather.com/docs/api/air-quality/aqi-coverage/

`qaqi` 覆盖全球任意地点；本地 AQI 仅在已接入国家/地区可用：欧洲多国 `eu-eea`（法国另有 `fr-atmo`）、英国 `gb-defra`、美国 `us-epa`、加拿大 `ca-eccc`、日本 `jp-moe`、韩国 `kr-moe`、新加坡 `sg-nea`、泰国 `th-pcd`，以及中国 `cn-mee`、中国香港 `hk-epd`、中国澳门 `mo-smg`、中国台湾省 `tw-me`。

## 健康影响和建议（health-effect-advice）

https://dev.qweather.com/docs/api/air-quality/health-effect-advice/

`health` 区分**一般人群**与**敏感人群**（老人、孕妇、儿童、心肺疾病患者、长期户外工作者等）。
> 健康建议非规范建议、不具法律效力，且不适用于所有国家和地区；如有不适请就医。

## 中国空气质量说明（china-aqi）

https://dev.qweather.com/docs/api/air-quality/china-aqi/

遵循《环境空气质量指数（AQI）技术规定》HJ 633—2026；中国地区暂不支持 `qaqi`，空气质量预报不支持污染物详细数据；分指数 < 50 时首要污染物为空。数据未经完整审核，仅供参考试。
