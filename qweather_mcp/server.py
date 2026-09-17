"""QWeather MCP server: stdio (默认) / streamable-http (--transport)。

API 对齐官方 mcp SDK 2.x (https://modelcontextprotocol.io/docs/develop/build-server):
`from mcp.server import MCPServer`, 2.0 起 FastMCP 更名为 MCPServer。
"""

import argparse
from datetime import datetime

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from qweather_mcp.client import QWeatherClient, get_client
from qweather_mcp.config import QWeatherConfigError
from qweather_mcp.formatting import build_report

mcp = MCPServer("qweather")


async def _located(location: str) -> tuple[QWeatherClient, dict]:
    """解析位置: 返回 (client, 含规范 lat/lon 的城市记录)。"""
    client = get_client()
    return client, await client.locate(location)


def _city_brief(location: dict) -> dict:
    return {
        "id": location.get("id"),
        "name": location.get("name"),
        "adm1": location.get("adm1"),
        "adm2": location.get("adm2"),
        "lat": location.get("lat"),
        "lon": location.get("lon"),
    }


def _today() -> str:
    return datetime.now().strftime("%Y%m%d")


def _id_or_coord(city: dict) -> str:
    """v7 类接口的 location: 优先 LocationID, 否则 经度,纬度。"""
    return city.get("id") or f"{city['lon']},{city['lat']}"


def _fmt_tz(utc_offset: str) -> str:
    """GeoAPI 的 "+08:00" -> 太阳高度角接口的 "0800"。"""
    return utc_offset.replace(":", "").lstrip("+")


@mcp.tool()
async def lookup_city(
    location: str,
    adm: str | None = None,
    country: str | None = None,
    number: int = 10,
) -> list[dict]:
    """搜索城市: 返回 Location ID、经纬度、行政区划等 (可多条)。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度" (如 "116.41,39.92")
        adm: 上级行政区划, 用于排除重名, 如 "辽宁"
        country: ISO 3166 国家代码, 如 "cn"; 不设则搜全球
        number: 返回条数 1-20, 默认 10
    """
    return await get_client().lookup_city(
        location, adm=adm, country=country, number=number
    )


@mcp.tool()
async def get_top_cities(
    country: str | None = None, number: int = 10
) -> list[dict]:
    """查询热门城市列表。

    Args:
        country: ISO 3166 国家代码, 如 "cn"; 不设则全球
        number: 返回条数 1-20, 默认 10
    """
    return await get_client().get_top_cities(country=country, number=number)


@mcp.tool()
async def lookup_poi(
    location: str,
    poi_type: str = "scenic",
    city: str | None = None,
    number: int = 10,
) -> list[dict]:
    """按关键字或坐标搜索 POI (景点 / 潮汐站点)。

    Args:
        location: 名称、LocationID, 或 "经度,纬度"
        poi_type: "scenic" 景点 (默认) 或 "TSTA" 潮汐站点
        city: 限定所在城市 (文字须精确匹配, 建议 LocationID); 默认不限制
        number: 返回条数 1-20, 默认 10
    """
    return await get_client().lookup_poi(
        location, poi_type, city=city, number=number
    )


@mcp.tool()
async def lookup_poi_range(
    location: str,
    poi_type: str = "scenic",
    radius: int = 5,
    number: int = 10,
) -> list[dict]:
    """按坐标半径搜索附近 POI。

    Args:
        location: "经度,纬度" (十进制, 最多两位小数), 如 "116.41,39.92"
        poi_type: "scenic" 景点 (默认) 或 "TSTA" 潮汐站点
        radius: 搜索半径公里, 1-50, 默认 5
        number: 返回条数 1-20, 默认 10
    """
    return await get_client().lookup_poi_range(
        location, poi_type, radius=radius, number=number
    )


@mcp.tool()
async def get_current_weather(
    location: str, local_time: bool = False
) -> dict:
    """实况天气 v1 (按经纬度, 全球任意地点): 天气现象、温度、体感、湿度、
    风向风速、阵风、降水、气压、能见度、露点、云量、紫外线。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
        local_time: True 返回当地时间, 默认 UTC
    """
    client, city = await _located(location)
    current = await client.get_current_v1(
        city["lat"], city["lon"], local_time=local_time
    )
    return {"city": _city_brief(city), "current": current}


@mcp.tool()
async def get_daily_forecast(
    location: str, days: int = 7, local_time: bool = False
) -> dict:
    """每日天气预报 v1 (最多 10 天): 白天/夜间天气、最高最低温、风、阵风、
    降水概率、紫外线、日出日落、月升月落与月相。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
        days: 预报天数 1-10, 默认 7
        local_time: True 返回当地时间, 默认 UTC
    """
    client, city = await _located(location)
    days_data = await client.get_daily_v1(
        city["lat"], city["lon"], days=days, local_time=local_time
    )
    return {"city": _city_brief(city), "days": days_data}


@mcp.tool()
async def get_hourly_forecast(
    location: str, hours: int = 24, local_time: bool = False
) -> dict:
    """小时天气预报 v1 (最多 240 小时): 逐小时温度、体感、湿度、风、阵风、
    降水概率、气压、能见度、露点、云量、紫外线。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
        hours: 预报小时数 1-240, 默认 24
        local_time: True 返回当地时间, 默认 UTC
    """
    client, city = await _located(location)
    hours_data = await client.get_hourly_v1(
        city["lat"], city["lon"], hours=hours, local_time=local_time
    )
    return {"city": _city_brief(city), "hours": hours_data}


@mcp.tool()
async def get_weather_indices(
    location: str, days: int = 1, types: str = "0"
) -> dict:
    """天气生活指数预报 (最多 3 天): 运动/洗车/穿衣/钓鱼/紫外线/旅游/花粉过敏/
    舒适度/感冒/空气污染扩散/空调/太阳镜/化妆/晾晒/交通/防晒。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
        days: 预报天数, 1 或 3, 默认 1
        types: 指数类型 ID, 逗号分隔如 "3,5"; "0" 表示全部, 默认 "0"。
            1 运动, 2 洗车, 3 穿衣, 4 钓鱼, 5 紫外线, 6 旅游(中国), 7 花粉过敏(中国),
            8 舒适度(中国), 9 感冒(中国), 10 空气污染扩散(中国), 11 空调(中国),
            12 太阳镜(中国), 13 化妆(中国), 14 晾晒(中国), 15 交通(中国), 16 防晒(中国)
    """
    client, city = await _located(location)
    daily = await client.get_indices(_id_or_coord(city), days=days, types=types)
    return {"city": _city_brief(city), "daily": daily}


@mcp.tool()
async def get_minutely_precipitation(location: str) -> dict:
    """分钟级降水 (临近预报, 仅中国): 未来 2 小时每 5 分钟降水量与类型,
    以及一句话摘要 (如「95分钟后雨就停了」)。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
    """
    client, city = await _located(location)
    data = await client.get_minutely(city["lat"], city["lon"])
    return {"city": _city_brief(city), **data}


@mcp.tool()
async def get_air_quality(location: str) -> dict:
    """实时空气质量: AQI 指数 (本地标准 + 通用 QAQI, 含等级/类别/首要污染物/
    健康建议) 与污染物浓度 (pm2.5/pm10/no2/o3/co/so2 等)。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
    """
    client, city = await _located(location)
    data = await client.get_air_current(city["lat"], city["lon"])
    return {"city": _city_brief(city), **data}


@mcp.tool()
async def get_air_quality_hourly(location: str) -> dict:
    """未来 24 小时逐小时空气质量预报: 每小时 AQI 指数与污染物浓度。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
    """
    client, city = await _located(location)
    hours = await client.get_air_hourly(city["lat"], city["lon"])
    return {"city": _city_brief(city), "hours": hours}


@mcp.tool()
async def get_air_quality_daily(location: str) -> dict:
    """未来 3 天每日空气质量预报: 每天 AQI 指数与污染物浓度。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
    """
    client, city = await _located(location)
    days = await client.get_air_daily(city["lat"], city["lon"])
    return {"city": _city_brief(city), "days": days}


@mcp.tool()
async def get_storm_list(year: int | None = None, basin: str = "NP") -> dict:
    """台风列表 (最近两年): ID、名称、年份、是否活跃。

    Args:
        year: 台风年份, 仅支持本年度或上一年度, 默认本年度
        basin: 流域, 目前仅支持 "NP" (西北太平洋)
    """
    client = get_client()
    target = year or datetime.now().year
    storms = await client.get_storm_list(basin, target)
    return {"basin": basin, "year": target, "storm": storms}


@mcp.tool()
async def get_storm_track(stormid: str) -> dict:
    """台风实况和路径: 当前位置/等级/气压/风速 (now, 已结束为 null) 与轨迹
    (track[]); isActive 表示是否活跃。

    Args:
        stormid: 台风 ID, 如 "NP2018" (来自 get_storm_list)
    """
    return await get_client().get_storm_track(stormid)


@mcp.tool()
async def get_storm_forecast(stormid: str) -> list[dict]:
    """台风预报: 预测位置/等级/气压/风速 (仅活跃台风, 已结束返回空)。

    Args:
        stormid: 台风 ID, 如 "NP2018" (来自 get_storm_list)
    """
    return await get_client().get_storm_forecast(stormid)


@mcp.tool()
async def get_tide(location: str, date: str | None = None) -> dict:
    """潮汐预报 (未来 10 天): 满潮/干潮时刻与高度表, 以及逐小时潮位。

    Args:
        location: 潮汐观测站 LocationID, 如 "P66981"
            (可用 lookup_poi(location=..., poi_type="TSTA") 按港口城市查到)
        date: 日期 yyyyMMdd, 今天起 10 天内, 默认今天
    """
    client = get_client()
    target = date or datetime.now().strftime("%Y%m%d")
    data = await client.get_tide(location, target)
    return {"location": location, "date": target, **data}


@mcp.tool()
async def get_sunrise_sunset(location: str, date: str | None = None) -> dict:
    """日出日落时间 (未来 60 天); 高纬度极昼/极夜时可能为空。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
        date: 日期 yyyyMMdd, 今天起 60 天内, 默认今天
    """
    client, city = await _located(location)
    target = date or _today()
    data = await client.get_sun(_id_or_coord(city), target)
    return {"city": _city_brief(city), "date": target, **data}


@mcp.tool()
async def get_moon(location: str, date: str | None = None) -> dict:
    """月升月落时间与逐小时月相 (未来 60 天, 高纬度/日期跨越时可能为空)。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
        date: 日期 yyyyMMdd, 今天起 60 天内, 默认今天
    """
    client, city = await _located(location)
    target = date or _today()
    data = await client.get_moon(_id_or_coord(city), target)
    return {"city": _city_brief(city), "date": target, **data}


@mcp.tool()
async def get_solar_elevation_angle(
    location: str,
    time: str,
    date: str | None = None,
    tz: str | None = None,
    alt: int = 0,
) -> dict:
    """指定时刻的太阳高度角与方位角 (方位角 0 度为正北), 及太阳时、时角。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
        time: 查询时间 HHmm (24 时制), 如 "1230"
        date: 日期 yyyyMMdd, 默认今天
        tz: 时区, 如 "0800" / "-0530"; 默认取该地点时区, 坐标入参需显式传入
        alt: 海拔高度 (米), 默认 0
    """
    client, city = await _located(location)
    target = f"{city['lon']},{city['lat']}"
    offset = city.get("utcOffset")
    resolved_tz = tz or (_fmt_tz(offset) if offset else None)
    if not resolved_tz:
        raise ToolError(
            "无法从该地点推断时区, 请显式传入 tz, 如 '0800' 或 '-0530'"
        )
    return await client.get_solar_elevation_angle(
        target, date or _today(), time, resolved_tz, alt
    )


@mcp.tool()
async def get_weather_alerts(
    location: str, local_time: bool = False
) -> dict:
    """正在生效的官方天气预警 (全球多数国家/地区): 事件类型、严重程度、颜色、
    生效/失效时间、详细描述与防御指南。无预警时 alerts 为空。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
        local_time: True 返回当地时间, 默认 UTC
    """
    client, city = await _located(location)
    data = await client.get_weather_alerts(
        city["lat"], city["lon"], local_time=local_time
    )
    return {"city": _city_brief(city), **data}


@mcp.tool()
async def get_weather_report(location: str) -> str:
    """生成格式统一的天气报告 Markdown (适合推送/通知场景直接发送):
    今日速览 + 三日预报 + 生活提示。要原始数据自行推理, 用
    get_daily_forecast / get_weather_indices 等工具。

    Args:
        location: 城市名、LocationID, 或 "经度,纬度", 如 "北京" / "116.41,39.92"
    """
    client, city = await _located(location)
    daily = await client.get_daily_v1(
        city["lat"], city["lon"], days=3, local_time=True
    )
    indices = await client.get_indices(_id_or_coord(city))
    return build_report(city.get("name") or location, daily, indices)


def main() -> None:
    parser = argparse.ArgumentParser(description="QWeather MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="stdio: 本地客户端 spawn (默认); streamable-http: 生产部署, 配 URL 即可",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8111)
    args = parser.parse_args()

    try:
        get_client()  # 提前校验配置, 失败信息直接可读
    except QWeatherConfigError as e:
        raise SystemExit(str(e)) from e

    if args.transport == "streamable-http":
        mcp.run(transport=args.transport, host=args.host, port=args.port)
    else:
        mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
