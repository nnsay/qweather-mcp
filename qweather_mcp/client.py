"""和风天气 API 客户端: JWT 签发 + 端点调用。

约定: 每个方法返回调用方直接使用的负载 —— 统一剥掉 `metadata`/`code` 信封,
集合类返回 `list`, 单对象返回 `dict`; 不把原始响应原样透出。

GeoAPI (docs/geoapi.md):
  - 城市搜索      GET /geo/v2/city/lookup
  - 热门城市      GET /geo/v2/city/top
  - POI 搜索      GET /geo/v2/poi/lookup
  - POI 范围搜索  GET /geo/v2/poi/range
天气预报 / 生活指数 (docs/weather.md):
  - 实时天气 v1   GET /weather/v1/current/{lat}/{lon}
  - 每日预报 v1   GET /weather/v1/daily/{lat}/{lon}
  - 小时预报 v1   GET /weather/v1/hourly/{lat}/{lon}
  - 生活指数      GET /v7/indices/{days}  (docs/indices.md)
  - 分钟级降水    GET /v7/minutely/5m  (docs/minutely.md)
空气质量 (docs/air-quality.md):
  - 实时空气质量  GET /airquality/v1/current/{lat}/{lon}
  - 空气质量小时  GET /airquality/v1/hourly/{lat}/{lon}
  - 空气质量每日  GET /airquality/v1/daily/{lat}/{lon}
热带气旋 / 台风 (docs/tropical-cyclone.md):
  - 台风列表      GET /v7/tropical/storm-list
  - 台风实况路径  GET /v7/tropical/storm-track
  - 台风预报      GET /v7/tropical/storm-forecast
海洋数据 (docs/ocean.md):
  - 潮汐          GET /v7/ocean/tide
天文 (docs/astronomy.md):
  - 日出日落      GET /v7/astronomy/sun
  - 月升月落月相  GET /v7/astronomy/moon
  - 太阳高度角    GET /v7/astronomy/solar-elevation-angle
预警 (docs/warning.md):
  - 实时天气预警  GET /weatheralert/v1/current/{lat}/{lon}
"""

import contextlib
import re
import time

import httpx
import jwt  # PyJWT
from mcp.server.mcpserver.exceptions import ToolError

from qweather_mcp.config import QWeatherConfig, load_config

JWT_TTL_SECONDS = 6 * 3600
# 过期前提前刷新, 避免请求途中刚好失效
JWT_REFRESH_MARGIN = 300
# 舒适度/穿衣/感冒/运动/紫外线/空气污染扩散/防晒
INDICES_TYPES = "1,3,5,8,9,10,16"
LANG = "zh"

# v1 天气接口的坐标路径参数最多两位小数
_COORD_RE = re.compile(r"^\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*$")

# 常见错误的可行动提示, 让 agent 知道下一步而不是只看到一个 4xx
_ERROR_HINTS = {
    400: "参数不合法或该地点无此数据 (部分接口未覆盖该国家/地区), 换城市/坐标或换工具",
    401: "认证失败: 检查 QWEATHER_PROJECT_ID / QWEATHER_CREDENTIAL_ID 与私钥是否匹配",
    403: "无权访问: 检查该凭据是否已订阅此 API",
    429: "请求超限 (频率/额度), 稍后重试",
    500: "和风服务端错误, 稍后重试",
    502: "和风网关错误, 稍后重试",
    503: "和风服务暂不可用, 稍后重试",
}


def _clamp_number(n: int) -> int:
    return max(1, min(20, n))


def _clamp_radius(km: int) -> int:
    return max(1, min(50, km))


def _clamp_days(n: int) -> int:
    return max(1, min(10, n))


def _clamp_hours(n: int) -> int:
    return max(1, min(240, n))


def _indices_days(days: int) -> str:
    return "3d" if days >= 3 else "1d"


def _fmt_coord(value: str) -> str:
    return f"{float(value):.2f}"


class QWeatherClient:
    def __init__(self, config: QWeatherConfig):
        self._config = config
        self._http = httpx.AsyncClient(
            base_url=config.api_base_url, timeout=15
        )
        self._jwt: str | None = None
        self._jwt_exp: int = 0
        # 私钥读一次就够, JWT 缓存到过期前再重签
        self._private_pem = config.private_key_path.read_text().strip()

    def _jwt_token(self) -> str:
        now = int(time.time())
        token = self._jwt
        if token is None or now >= self._jwt_exp - JWT_REFRESH_MARGIN:
            self._jwt_exp = now + JWT_TTL_SECONDS
            token = jwt.encode(
                payload={
                    "sub": self._config.project_id,
                    "iat": now,
                    "exp": self._jwt_exp,
                },
                key=self._private_pem,
                algorithm="EdDSA",
                headers={"kid": self._config.credential_id},
            )
            self._jwt = token
        return token

    async def _get(
        self, path: str, **params: str | int | None
    ) -> dict:
        query = {
            "lang": LANG,
            **{k: str(v) for k, v in params.items() if v is not None},
        }
        resp = await self._http.get(
            path,
            params=query,
            headers={"Authorization": f"Bearer {self._jwt_token()}"},
        )
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            # 和风错误详情在响应体 {"error": {"title": ...}} 里, 提出来更好定位
            detail = ""
            with contextlib.suppress(Exception):  # 解析失败就用 reason phrase
                detail = e.response.json().get("error", {}).get("title", "")
            code = e.response.status_code
            hint = _ERROR_HINTS.get(code)
            msg = f"和风天气 API {code}: {detail or e.response.reason_phrase}"
            if hint:
                msg += f" ({hint})"
            # 用 ToolError 而非 RuntimeError: SDK 只把 ToolError 的消息透给模型,
            # 其它异常会被包成笼统的 "Error executing tool ..." (见 tools/base.py)。
            raise ToolError(msg) from e
        return resp.json()

    async def lookup_city(
        self,
        location: str,
        *,
        adm: str | None = None,
        country: str | None = None,
        number: int = 10,
    ) -> list[dict]:
        """城市搜索: 名称 / LocationID / 经度,纬度。country 为 ISO 3166 代码。"""
        data = await self._get(
            "/geo/v2/city/lookup",
            location=location,
            adm=adm,
            range=country,
            number=str(_clamp_number(number)),
        )
        return data.get("location") or []

    async def search_city(self, city: str) -> dict | None:
        """城市搜索, 返回首个匹配, 未找到返回 None。天气类工具内部用。"""
        locations = await self.lookup_city(city, number=1)
        return locations[0] if locations else None

    async def locate(self, location: str) -> dict:
        """解析位置, 返回带 lat/lon 的记录 (坐标规范为两位小数)。

        location 为 "经度,纬度" 时直接采用 (不经过 GeoAPI, 支持任意地点);
        否则当作城市名/ LocationID 走 GeoAPI 搜索首个匹配。未找到抛 ValueError。
        """
        if _COORD_RE.match(location):
            lon, lat = (part.strip() for part in location.split(","))
            return {"name": location, "lat": _fmt_coord(lat), "lon": _fmt_coord(lon)}
        found = await self.search_city(location)
        if not found:
            raise ToolError(f"未找到位置: {location}")
        return {
            **found,
            "lat": _fmt_coord(found["lat"]),
            "lon": _fmt_coord(found["lon"]),
        }

    async def get_top_cities(
        self, *, country: str | None = None, number: int = 10
    ) -> list[dict]:
        """热门城市列表。country 为 ISO 3166 代码, 不设则全球。"""
        data = await self._get(
            "/geo/v2/city/top",
            range=country,
            number=str(_clamp_number(number)),
        )
        return data.get("topCityList") or []

    async def lookup_poi(
        self,
        location: str,
        poi_type: str,
        *,
        city: str | None = None,
        number: int = 10,
    ) -> list[dict]:
        """POI 搜索。poi_type: scenic 景点 / TSTA 潮汐站点。"""
        data = await self._get(
            "/geo/v2/poi/lookup",
            location=location,
            type=poi_type,
            city=city,
            number=str(_clamp_number(number)),
        )
        return data.get("poi") or []

    async def lookup_poi_range(
        self,
        location: str,
        poi_type: str,
        *,
        radius: int = 5,
        number: int = 10,
    ) -> list[dict]:
        """POI 范围搜索。location 必须是 经度,纬度。radius 1-50 公里。"""
        data = await self._get(
            "/geo/v2/poi/range",
            location=location,
            type=poi_type,
            radius=str(_clamp_radius(radius)),
            number=str(_clamp_number(number)),
        )
        return data.get("poi") or []

    async def get_indices(
        self,
        location: str,
        *,
        days: int = 1,
        types: str = INDICES_TYPES,
    ) -> list[dict]:
        """生活指数预报 (最多 3 天)。types: 逗号分隔的类型 ID, "0" 为全部。

        location 可为 LocationID 或 "经度,纬度"。
        """
        data = await self._get(
            f"/v7/indices/{_indices_days(days)}",
            location=location,
            type=types,
        )
        return data.get("daily") or []

    async def get_current_v1(
        self, lat: str, lon: str, *, local_time: bool = False
    ) -> dict:
        """实时天气 v1 (经纬度)。详见 docs/weather.md。"""
        data = await self._get(
            f"/weather/v1/current/{lat}/{lon}",
            localTime="true" if local_time else None,
        )
        data.pop("metadata", None)
        return data

    async def get_daily_v1(
        self, lat: str, lon: str, *, days: int = 7, local_time: bool = False
    ) -> list[dict]:
        """每日天气预报 v1 (最多 10 天)。"""
        data = await self._get(
            f"/weather/v1/daily/{lat}/{lon}",
            days=str(_clamp_days(days)),
            localTime="true" if local_time else None,
        )
        return data.get("days") or []

    async def get_hourly_v1(
        self, lat: str, lon: str, *, hours: int = 24, local_time: bool = False
    ) -> list[dict]:
        """小时天气预报 v1 (最多 240 小时)。"""
        data = await self._get(
            f"/weather/v1/hourly/{lat}/{lon}",
            hours=str(_clamp_hours(hours)),
            localTime="true" if local_time else None,
        )
        return data.get("hours") or []

    async def get_minutely(self, lat: str, lon: str) -> dict:
        """分钟级降水 (中国, 未来 2 小时每 5 分钟): summary + minutely[]。"""
        data = await self._get("/v7/minutely/5m", location=f"{lon},{lat}")
        return {"summary": data.get("summary"), "minutely": data.get("minutely") or []}

    async def get_air_current(self, lat: str, lon: str) -> dict:
        """实时空气质量 (经纬度): indexes[] + pollutants[]。"""
        data = await self._get(f"/airquality/v1/current/{lat}/{lon}")
        return {
            "indexes": data.get("indexes") or [],
            "pollutants": data.get("pollutants") or [],
        }

    async def get_air_hourly(self, lat: str, lon: str) -> list[dict]:
        """未来 24 小时逐小时空气质量。"""
        data = await self._get(f"/airquality/v1/hourly/{lat}/{lon}")
        return data.get("hours") or []

    async def get_air_daily(self, lat: str, lon: str) -> list[dict]:
        """未来 3 天每日空气质量。"""
        data = await self._get(f"/airquality/v1/daily/{lat}/{lon}")
        return data.get("days") or []

    async def get_storm_list(self, basin: str, year: int) -> list[dict]:
        """台风列表 (最近 2 年, 目前仅 basin=NP 西北太平洋)。"""
        data = await self._get(
            "/v7/tropical/storm-list", basin=basin, year=str(year)
        )
        return data.get("storm") or []

    async def get_storm_track(self, stormid: str) -> dict:
        """台风实况与路径: isActive / now (已结束为 null) / track[]。"""
        data = await self._get(
            "/v7/tropical/storm-track", stormid=stormid
        )
        return {
            "isActive": data.get("isActive"),
            "now": data.get("now"),
            "track": data.get("track") or [],
        }

    async def get_storm_forecast(self, stormid: str) -> list[dict]:
        """台风预报 (仅活跃台风, 已结束返回空)。"""
        data = await self._get(
            "/v7/tropical/storm-forecast", stormid=stormid
        )
        return data.get("forecast") or []

    async def get_tide(self, location: str, date: str) -> dict:
        """潮汐 (未来 10 天): location 为潮汐站 LocationID, date 为 yyyyMMdd。"""
        data = await self._get(
            "/v7/ocean/tide", location=location, date=date
        )
        return {
            "tideTable": data.get("tideTable") or [],
            "tideHourly": data.get("tideHourly") or [],
        }

    async def get_sun(self, location: str, date: str) -> dict:
        """日出日落 (未来 60 天, 高纬度可能为空)。location 为 ID 或 经度,纬度。"""
        data = await self._get(
            "/v7/astronomy/sun", location=location, date=date
        )
        return {"sunrise": data.get("sunrise"), "sunset": data.get("sunset")}

    async def get_moon(self, location: str, date: str) -> dict:
        """月升月落与逐小时月相 (未来 60 天)。"""
        data = await self._get(
            "/v7/astronomy/moon", location=location, date=date
        )
        return {
            "moonrise": data.get("moonrise"),
            "moonset": data.get("moonset"),
            "moonPhase": data.get("moonPhase") or [],
        }

    async def get_solar_elevation_angle(
        self, location: str, date: str, time: str, tz: str, alt: int
    ) -> dict:
        """指定时刻的太阳高度角/方位角。location 仅支持 经度,纬度。"""
        return await self._get(
            "/v7/astronomy/solar-elevation-angle",
            location=location,
            date=date,
            time=time,
            tz=tz,
            alt=str(alt),
        )

    async def get_weather_alerts(
        self, lat: str, lon: str, *, local_time: bool = False
    ) -> dict:
        """正在生效的官方天气预警: zeroResult + alerts[]。"""
        data = await self._get(
            f"/weatheralert/v1/current/{lat}/{lon}",
            localTime="true" if local_time else None,
        )
        return {
            "zeroResult": data.get("metadata", {}).get("zeroResult"),
            "alerts": data.get("alerts") or [],
        }


_client: QWeatherClient | None = None


def get_client() -> QWeatherClient:
    """进程级单例; 首次调用时加载配置, 配置错误即刻失败。"""
    global _client
    if _client is None:
        _client = QWeatherClient(load_config())
    return _client
