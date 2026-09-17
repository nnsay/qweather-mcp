# 天气预报 (Weather)

来源: https://dev.qweather.com/docs/api/weather/

和风有两套天气 API：

- **v1（推荐）**：按经纬度查询，全球任意地点，1 公里分辨率。分实时 / 每日 / 每小时。
- **WebAPI v7（官方标注「即将弃用」）**：按 LocationID 查询城市。`now` / `{days}d` / `{hours}`。

认证：`Authorization: Bearer <JWT>`。Host 为专属 API Host。本文档按 v1 实现；v7 仅作字段参考。

## 实时天气 v1

https://dev.qweather.com/docs/api/weather/weather-current/

```
GET /weather/v1/current/{latitude}/{longitude}
```

路径参数 `latitude` / `longitude`：十进制，最多两位小数（如 `39.92` / `116.41`）。
查询参数 `localTime`：`false` UTC（默认）/ `true` 本地时间。

响应：`condition{text,code}`、`temperature{value,unit}`、`feelsLike`、`humidity [0,1]`、
`wind{direction{degree,compass},speed{value,unit},scale}`、`windGust`、
`precipitation{amount,intensity,type}`、`pressure`、`visibility`、`dewPoint`、`cloudCover [0,1]`、`uvIndex [0,15]`。

## 每日天气预报 v1

https://dev.qweather.com/docs/api/weather/weather-daily-forecast/

```
GET /weather/v1/daily/{latitude}/{longitude}
```

查询参数 `days`：`1-10`，默认 `7`。

响应 `days[]`：`forecastStartTime/EndTime`、`astro{日出日落/晨昏/月升月落/月相}`
（`moonPhase` 取值 `new-moon`…`waning-crescent`）、`temperatureMax/Min/Avg`、`uvIndexMax`、
`daytime{condition, temperatureMax/Min, humidity, wind, windGustMax, precipitation{amount,type,probability}, cloudCover}`、
`nighttime{同上}`。白天 `[07:00,19:00)`、夜间 `[19:00,次日07:00)` 当地时间。

## 小时天气预报 v1

https://dev.qweather.com/docs/api/weather/weather-hourly-forecast/

```
GET /weather/v1/hourly/{latitude}/{longitude}
```

查询参数 `hours`：`1-240`，默认 `24`。

响应 `hours[]`：`forecastTime`、`condition`、`temperature`、`feelsLike`、`humidity`、
`wind`、`windGust`、`precipitation{amount,intensity,probability,type}`、`pressure`、
`visibility`、`dewPoint`、`cloudCover`、`uvIndex`。

## 城市实时天气 v7（弃用）

https://dev.qweather.com/docs/api/weather/weather-now-webapi-v7/

```
GET /v7/weather/now?location={id|经度,纬度}
```

响应 `now`：`obsTime,temp,feelsLike,icon,text,wind360,windDir,windScale,windSpeed,humidity,precip,pressure,vis,cloud,dew`。

## 城市每日预报 v7（弃用）

https://dev.qweather.com/docs/api/weather/weather-daily-forecast-webapi-v7/

```
GET /v7/weather/{days}?location={id|经度,纬度}
```

`days` 取值 `3d` / `7d` / `10d` / `15d` / `30d`。

响应 `daily[]`：`fxDate,sunrise,sunset,moonrise,moonset,moonPhase,moonPhaseIcon,tempMax,tempMin,
iconDay,textDay,iconNight,textNight,wind360Day,windDirDay,windScaleDay,windSpeedDay,
wind360Night,windDirNight,windScaleNight,windSpeedNight,humidity,precip,pressure,vis,cloud,uvIndex`。

## 城市小时预报 v7（弃用）

https://dev.qweather.com/docs/api/weather/weather-hourly-forecast-webapi-v7/

```
GET /v7/weather/{hours}?location={id|经度,纬度}
```

`hours` 取值 `24h` / `72h` / `168h`。

响应 `hourly[]`：`fxTime,temp,icon,text,wind360,windDir,windScale,windSpeed,humidity,pop,precip,pressure,cloud,dew`。

## 天气现象代码

https://dev.qweather.com/docs/api/weather/weather-conditions/

| code | text | code | text |
| --- | --- | --- | --- |
| 100 | 晴 | 101 | 多云 |
| 102 | 少云 | 103 | 晴间多云 |
| 104 | 阴 | 300 | 阵雨 |
| 301 | 强阵雨 | 302 | 雷阵雨 |
| 303 | 强雷阵雨 | 304 | 雷阵雨伴有冰雹 |
| 305 | 小雨 | 306 | 中雨 |
| 307 | 大雨 | 308 | 极端降雨 |
| 309 | 毛毛雨/细雨 | 310 | 暴雨 |
| 311 | 大暴雨 | 312 | 特大暴雨 |
| 313 | 冻雨 | 314 | 小到中雨 |
| 315 | 中到大雨 | 316 | 大到暴雨 |
| 317 | 暴雨到大暴雨 | 318 | 大暴雨到特大暴雨 |
| 399 | 雨 | 400 | 小雪 |
| 401 | 中雪 | 402 | 大雪 |
| 403 | 暴雪 | 404 | 雨夹雪 |
| 405 | 雨雪天气 | 406 | 阵雨夹雪 |
| 407 | 阵雪 | 408 | 小到中雪 |
| 409 | 中到大雪 | 410 | 大到暴雪 |
| 499 | 雪 | 500 | 薄雾 |
| 501 | 雾 | 502 | 霾 |
| 503 | 扬沙 | 504 | 浮尘 |
| 507 | 沙尘暴 | 508 | 强沙尘暴 |
| 509 | 浓雾 | 510 | 强浓雾 |
| 511 | 中度霾 | 512 | 重度霾 |
| 513 | 严重霾 | 514 | 大雾 |
| 515 | 特强浓雾 | 900 | 热 |
| 901 | 冷 | 999 | 未知 |

## 风向与风力

https://dev.qweather.com/docs/api/weather/wind-guide/

v1 `wind.direction.compass`（16 方位代码）：`n,nne,ne,ene,e,ese,se,sse,s,ssw,sw,wsw,w,wnw,nw,nnw,none,vrb`；
`degree` 以正北 0° 顺时针，`[0,359]`，无主导风向为 `null`。
v7 `windDir` 在中文本地化下直接返回中文方位（如「西北风」）。

蒲福风级（`scale`，0-12；13-17 为热带气旋扩展）：

| 级 | 术语 | 风速 (m/s) |
| --- | --- | --- |
| 0 | 无风 | < 0.5 |
| 1 | 软风 | 0.5–1.5 |
| 2 | 轻风 | 1.6–3.3 |
| 3 | 微风 | 3.4–5.5 |
| 4 | 和风 | 5.5–7.9 |
| 5 | 清风 | 8.0–10.7 |
| 6 | 强风 | 10.8–13.8 |
| 7 | 疾风 | 13.9–17.1 |
| 8 | 大风 | 17.2–20.7 |
| 9 | 烈风 | 20.8–24.4 |
| 10 | 狂风 | 24.5–28.4 |
| 11 | 暴风 | 28.5–32.6 |
| 12 | 飓风 | ≥ 32.7 |
