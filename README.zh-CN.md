# qweather-mcp

[English](README.md) | [中文](README.zh-CN.md)

和风天气 (QWeather) MCP server。官方 `mcp` SDK 2.x（`MCPServer`）实现，stdio / streamable-http 双 transport，凭证收敛在服务端进程，客户端只见 `location` 参数。

## 工具

| 工具 | 返回 | 用途 |
| --- | --- | --- |
| `lookup_city(location, adm?, country?, number?)` | 城市列表 (id/经纬度/行政区) | Geo: 城市搜索 / 坐标反查 |
| `get_top_cities(country?, number?)` | 热门城市列表 | Geo: 各国热门城市 |
| `lookup_poi(location, poi_type, city?, number?)` | POI 列表 | Geo: 景点 / 潮汐站点搜索 |
| `lookup_poi_range(location, poi_type, radius?, number?)` | POI 列表 | Geo: 坐标半径内 POI |
| `get_current_weather(location, local_time?)` | 实况 JSON（城市 + v1 current） | 当前天气（全球经纬度） |
| `get_daily_forecast(location, days?, local_time?)` | 预报 JSON（城市 + v1 days[]） | 每日预报（最多 10 天） |
| `get_hourly_forecast(location, hours?, local_time?)` | 预报 JSON（城市 + v1 hours[]） | 小时预报（最多 240 小时） |
| `get_minutely_precipitation(location)` | 城市 + 摘要 + 5 分钟降水序列 | 分钟级降水（仅中国，未来 2 小时） |
| `get_weather_indices(location, days?, types?)` | 城市 + 指数列表（含说明） | 生活指数（1/3 天，可选类型） |
| `get_air_quality(location)` | 城市 + AQI 指数 + 污染物 | 实时空气质量（含健康建议） |
| `get_air_quality_hourly(location)` | 城市 + 逐小时 AQI/污染物 | 空气质量小时预报（24h） |
| `get_air_quality_daily(location)` | 城市 + 逐日 AQI/污染物 | 空气质量每日预报（3d） |
| `get_storm_list(year?, basin?)` | 台风 ID/名称/年份/是否活跃 | 台风列表（近两年，NP） |
| `get_storm_track(stormid)` | 实况 `now` + 轨迹 `track` | 台风实况和路径 |
| `get_storm_forecast(stormid)` | 预测位置/等级/气压/风速 | 台风预报（活跃台风） |
| `get_tide(location, date?)` | 满潮/干潮 + 逐小时潮位 | 潮汐（未来 10 天） |
| `get_sunrise_sunset(location, date?)` | 日出/日落时间 | 天文·日出日落（60 天） |
| `get_moon(location, date?)` | 月升/月落 + 逐小时月相 | 天文·月相（60 天） |
| `get_solar_elevation_angle(location, time, date?, tz?, alt?)` | 太阳高度角/方位角 | 天文·太阳高度角 |
| `get_weather_alerts(location, local_time?)` | 生效中的官方预警列表 | 预警（全球多数国家） |
| `get_weather_report(location)` | 成品 Markdown（今日速览 + 三日预报 + 生活提示） | 推送、通知场景直接发送 |

`location` 支持城市名、LocationID 或 `"经度,纬度"`（如 `"116.41,39.92"`）。天气类工具按 v1 经纬度查询，1 公里分辨率覆盖全球；`get_weather_report` 直接用 v1 每日预报生成。仍走 v7 的只剩生活指数（`/v7/indices`，官方无 v1 版本）。

和风端点与官方文档对照见 [`docs/`](docs/)。新增 API = `client.py` 加一个方法 + `server.py` 加一个 `@mcp.tool()`。

## 配置

**一律环境变量**（12-factor），没有配置文件；CLI 参数只管运行方式（`--transport/--host/--port`）。缺失必填项启动即失败并指明缺哪个。

| 变量 | 说明 |
| --- | --- |
| `QWEATHER_API_HOST` | 专属 API host，如 `your-host.re.qweatherapi.com`（必填） |
| `QWEATHER_PROJECT_ID` | 项目 ID，JWT `sub`（必填） |
| `QWEATHER_CREDENTIAL_ID` | 凭据 ID，JWT `kid`（必填） |
| `QWEATHER_PRIVATE_KEY_PATH` | Ed25519 私钥路径，默认 `~/.ssh/ed25519-private.pem` |

私钥只存在于文件系统（`~/.ssh/`），不进任何客户端配置文件、不进 LLM 上下文；客户端配置里只有 host 和两个非机密 ID。

## 运行

安装为全局工具：

```bash
uv tool install .
```

```bash
# stdio（默认，本地客户端 spawn）
qweather-mcp

# streamable-http（共享服务部署，客户端只配 URL）
qweather-mcp --transport streamable-http --host 0.0.0.0 --port 8111
```

代码更新后需重装：`uv tool install --force .`；开发期想要改码即生效可用 `uv tool install -e .`（可编辑安装）。

开发期快速跑 streamable-http：

```bash
uv run qweather-mcp --transport streamable-http   # 默认 127.0.0.1:8111/mcp
```

## 各端接入

**Claude Code**（项目 `.mcp.json`）：

```json
{
  "mcpServers": {
    "qweather": {
      "command": "/Users/you/.local/bin/qweather-mcp",
      "env": {
        "QWEATHER_API_HOST": "<你的专属 API host>",
        "QWEATHER_PROJECT_ID": "<项目 ID>",
        "QWEATHER_CREDENTIAL_ID": "<凭据 ID>"
      }
    }
  }
}
```

**其他 MCP 客户端**（Claude Desktop、Gemini、各类 agent）：在各自 MCP 配置里填同一份 `command` + 上面 3 个 env。

**共享服务模式**：运行 `qweather-mcp --transport streamable-http --host 0.0.0.0 --port 8111`，在支持 streamable-http 的客户端（如 LangChain/LangGraph `load_mcp_tools`）里注册 `http://127.0.0.1:8111/mcp`。生产部署建议做网络隔离（仅集群内可达）。

**容器部署**：容器内 `uv tool install .`（或 pip install）后运行 `qweather-mcp --transport streamable-http`；配置全走容器 env，私钥文件挂载 secret 后用 `QWEATHER_PRIVATE_KEY_PATH` 指向。

## 许可证

[MIT](LICENSE)
