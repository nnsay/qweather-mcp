"""天气报告 Markdown 生成 (移植自 qweather skill 的 examples/sample.md 输出规范)。

输入为 v1 每日预报 (docs/weather.md): ``days[]`` 的 ``daytime/condition``、
``temperatureMin/Max``、``daytime/wind`` 等嵌套字段。生活指数仍来自 v7
``/v7/indices`` (该接口无 v1 版本)。所有取值都容错: 字段缺失只显示占位符,
不让报告生成中途抛异常。
"""

from typing import Any

# 城市标题 emoji: 按今日白天天气状况选择; 子串匹配, 顺序即优先级
_WEATHER_EMOJI_RULES: list[tuple[tuple[str, ...], str]] = [
    (("雨夹雪", "阵雪", "小雪", "中雪", "大雪", "暴雪"), "🌨️"),
    (("雷阵雨", "大雨", "暴雨"), "⛈️"),
    (("小雨", "中雨", "阵雨"), "🌧️"),
    (("沙尘", "浮尘", "扬沙"), "🌪️"),
    (("雾", "霾"), "🌫️"),
    (("阴",), "🌥️"),
    (("多云",), "☁️"),
    (("晴",), "🌤️"),
]
DEFAULT_WEATHER_EMOJI = "☁️"

# v1 风引用 compass 方位代码 (docs/weather.md), 报告里转成中文
_COMPASS_CN = {
    "n": "北风",
    "nne": "东北偏北风",
    "ne": "东北风",
    "ene": "东北偏东风",
    "e": "东风",
    "ese": "东南偏东风",
    "se": "东南风",
    "sse": "东南偏南风",
    "s": "南风",
    "ssw": "西南偏南风",
    "sw": "西南风",
    "wsw": "西南偏西风",
    "w": "西风",
    "wnw": "西北偏西风",
    "nw": "西北风",
    "nnw": "西北偏北风",
    "vrb": "风向不定",
    "none": "无持续风向",
}

_INDEX_ICONS = {
    "舒适度": "😊",
    "穿衣": "👕",
    "感冒": "🤧",
    "运动": "🏃",
    "紫外线": "☀️",
    "空气污染扩散": "🌫️",
    "防晒": "🧴",
}
_DEFAULT_INDEX_ICON = "🔹"

# sample.md 规范顺序; API 返回顺序不保证, 按此重排
_INDEX_ORDER = {name: rank for rank, name in enumerate(_INDEX_ICONS)}

_DAY_LABELS = ("今天", "明天", "后天")


def _dig(obj: object, *keys: str) -> Any:
    """逐层安全取字典字段, 任一层不是 dict 或缺失就返回 None。"""
    cur: Any = obj
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _num(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _round_temp(value: object) -> str:
    n = _num(value)
    return "?" if n is None else f"{round(n)}"


def weather_emoji(text_day: str) -> str:
    for keywords, emoji in _WEATHER_EMOJI_RULES:
        if any(kw in text_day for kw in keywords):
            return emoji
    return DEFAULT_WEATHER_EMOJI


def index_icon(name: str) -> str:
    # API 返回的名字带 "指数"/"条件指数" 后缀 (如 "空气污染扩散条件指数"), 用子串匹配
    for key, icon in _INDEX_ICONS.items():
        if key in name:
            return icon
    return _DEFAULT_INDEX_ICON


def _index_rank(name: str) -> int:
    for key, rank in _INDEX_ORDER.items():
        if key in name:
            return rank
    return len(_INDEX_ORDER)


def _day_text(day: dict) -> str:
    return _dig(day, "daytime", "condition", "text") or ""


def _temp_value(day: dict, key: str) -> object:
    value = _dig(day, key)
    return value.get("value") if isinstance(value, dict) else value


def _day_wind(day: dict) -> tuple[str, str]:
    wind = _dig(day, "daytime", "wind") or {}
    compass = _dig(wind, "direction", "compass")
    direction = _COMPASS_CN.get(compass, compass or "")
    scale = _dig(wind, "scale")
    return direction, ("?" if scale is None else f"{scale} 级")


def _mm_dd(day: dict) -> str:
    return str(_dig(day, "forecastStartTime") or "")[5:10]


def _day_line(day: dict, label: str) -> str:
    direction, scale = _day_wind(day)
    return (
        f"- {label} ({_mm_dd(day)}): {_day_text(day)}，"
        f"{_round_temp(_temp_value(day, 'temperatureMin'))}~"
        f"{_round_temp(_temp_value(day, 'temperatureMax'))}°C，"
        f"{direction} {scale}"
    )


def _temp_diff(day: dict) -> float:
    high = _num(_temp_value(day, "temperatureMax"))
    low = _num(_temp_value(day, "temperatureMin"))
    if high is None or low is None:
        return 0.0
    return high - low


def _today_summary(day: dict) -> str:
    text = _day_text(day)
    direction, scale = _day_wind(day)
    line = (
        f"{text}，"
        f"{_round_temp(_temp_value(day, 'temperatureMin'))}~"
        f"{_round_temp(_temp_value(day, 'temperatureMax'))}°C，"
        f"{direction} {scale}。"
    )
    if "雨" in text or "雪" in text:
        line += "出门记得带伞，注意保暖。"
    elif _temp_diff(day) >= 10:
        line += "昼夜温差大，早晚注意保暖。"
    return line


def _advice(daily: list[dict]) -> str:
    if not daily:
        return "暂无天气数据。"
    today = daily[0]
    text = _day_text(today)
    diff = _temp_diff(today)
    if "雪" in text:
        return "今天有雪，路面易结冰，出行注意防滑。"
    if "雨" in text:
        return "今天有雨，路面湿滑，出行注意安全。"
    if diff >= 10:
        return f"昼夜温差达 {round(diff)}°C，推荐洋葱式穿衣法。"
    if "雾" in text or "霾" in text:
        return "今天能见度较低，出行注意交通安全。"
    return "天气平稳，适合户外活动。"


def build_report(city_name: str, daily: list[dict], indices: list[dict]) -> str:
    """按 sample.md 规范生成天气报告 Markdown。

    daily: v1 每日预报 ``days[]`` (今天起 3 天);
    indices: v7 ``/v7/indices/1d`` 的 ``daily[]`` (7 项)。
    """
    today = daily[0] if daily else {}
    lines = [
        f"### {weather_emoji(_day_text(today))} {city_name}天气",
        "",
        "#### 📌 今日速览",
        "",
        _today_summary(today),
        "",
        "#### 📅 三日预报",
        "",
        *[
            _day_line(day, label)
            for day, label in zip(daily, _DAY_LABELS, strict=False)
        ],
        "",
        "#### 💡 生活提示",
        "",
        *[
            f"- {index_icon(item.get('name', ''))} {item.get('name', '')}："
            f"{item.get('category', '')}，{item.get('text', '')}"
            for item in sorted(indices, key=lambda it: _index_rank(it.get("name", "")))
        ],
        "",
        "#### 🔔 温馨提示",
        "",
        _advice(daily),
    ]
    return "\n".join(lines)
