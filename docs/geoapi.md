# GeoAPI

来源: https://dev.qweather.com/docs/api/geoapi/

天气数据基于地理位置。GeoAPI 提供城市/POI 的 Location ID、多语言名称、经纬度、时区、海拔、Rank、上级行政区等。支持名称模糊搜索、经纬度反查，无需自维护城市列表。

认证: `Authorization: Bearer <JWT>`。Host 为专属 API Host。

## 城市搜索

https://dev.qweather.com/docs/api/geoapi/city-lookup/

```
GET /geo/v2/city/lookup
```

| 参数 | 必选 | 说明 |
| --- | --- | --- |
| location | 是 | 地区名称、LocationID，或 `经度,纬度`（十进制）。如 `101010100` 或 `116.41,39.92` |
| adm | 否 | 上级行政区划，用于排除重名。如 `adm=beijing` |
| range | 否 | 搜索范围，ISO 3166 国家代码。不设则搜全球。如 `range=cn` |
| number | 否 | 返回条数 1-20，默认 10 |
| lang | 否 | 多语言 |

响应 `location[]`: name, id, lat, lon, adm2, adm1, country, tz, utcOffset, isDst, type, rank, fxLink。

## 热门城市查询

https://dev.qweather.com/docs/api/geoapi/top-city/

```
GET /geo/v2/city/top
```

| 参数 | 必选 | 说明 |
| --- | --- | --- |
| range | 否 | ISO 3166 国家代码。不设则全球 |
| number | 否 | 返回条数 1-20，默认 10 |
| lang | 否 | 多语言 |

响应 `topCityList[]`: 字段同城市搜索的 location 项。

## POI 搜索

https://dev.qweather.com/docs/api/geoapi/poi-lookup/

```
GET /geo/v2/poi/lookup
```

| 参数 | 必选 | 说明 |
| --- | --- | --- |
| location | 是 | 名称、LocationID 或 `经度,纬度` |
| type | 是 | `scenic` 景点 / `TSTA` 潮汐站点 |
| city | 否 | 限定城市（文字或 LocationID，文字须精确匹配）。默认不限制 |
| number | 否 | 返回条数 1-20，默认 10 |
| lang | 否 | 多语言 |

响应 `poi[]`: 字段同城市搜索的 location 项，type 为 scenic/TSTA。

## POI 范围搜索

https://dev.qweather.com/docs/api/geoapi/poi-range/

```
GET /geo/v2/poi/range
```

| 参数 | 必选 | 说明 |
| --- | --- | --- |
| location | 是 | `经度,纬度`（十进制，最多小数点后两位）。如 `116.41,39.92` |
| type | 是 | `scenic` / `TSTA` |
| radius | 否 | 搜索半径公里，1-50，默认 5 |
| number | 否 | 返回条数 1-20，默认 10 |
| lang | 否 | 多语言 |

响应 `poi[]`: 同 POI 搜索。
