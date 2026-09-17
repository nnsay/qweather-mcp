# qweather-mcp

[English](README.md) | [中文](README.zh-CN.md)

A [QWeather](https://www.qweather.com/) MCP server built on the official `mcp` SDK 2.x (`MCPServer`), with both **stdio** and **streamable-http** transports. Credentials stay in the server process — clients only ever pass a `location` parameter.

## Tools

| Tool | Returns | Use case |
| --- | --- | --- |
| `lookup_city(location, adm?, country?, number?)` | City list (id / lat-lon / admin region) | Geo: city search / coordinate lookup |
| `get_top_cities(country?, number?)` | Top cities list | Geo: top cities per country |
| `lookup_poi(location, poi_type, city?, number?)` | POI list | Geo: attractions / tide station search |
| `lookup_poi_range(location, poi_type, radius?, number?)` | POI list | Geo: POIs within a radius |
| `get_current_weather(location, local_time?)` | Nowcast JSON (city + v1 current) | Current weather (global lat-lon) |
| `get_daily_forecast(location, days?, local_time?)` | Forecast JSON (city + v1 days[]) | Daily forecast (up to 10 days) |
| `get_hourly_forecast(location, hours?, local_time?)` | Forecast JSON (city + v1 hours[]) | Hourly forecast (up to 240 hours) |
| `get_minutely_precipitation(location)` | City + summary + 5-min precipitation series | Minutely precipitation (China only, next 2 hours) |
| `get_weather_indices(location, days?, types?)` | City + indices list (with descriptions) | Life indices (1/3 days, optional types) |
| `get_air_quality(location)` | City + AQI + pollutants | Real-time air quality (with health advice) |
| `get_air_quality_hourly(location)` | City + hourly AQI/pollutants | Air quality hourly forecast (24h) |
| `get_air_quality_daily(location)` | City + daily AQI/pollutants | Air quality daily forecast (3d) |
| `get_storm_list(year?, basin?)` | Typhoon id / name / year / active | Typhoon list (last 2 years, NP basin) |
| `get_storm_track(stormid)` | Nowcast `now` + track `track` | Typhoon real-time and track |
| `get_storm_forecast(stormid)` | Forecast position / grade / pressure / wind | Typhoon forecast (active storms) |
| `get_tide(location, date?)` | High/low tides + hourly sea level | Tides (next 10 days) |
| `get_sunrise_sunset(location, date?)` | Sunrise / sunset times | Astronomy: sunrise & sunset (60 days) |
| `get_moon(location, date?)` | Moonrise / moonset + hourly phases | Astronomy: moonrise, moonset & phase (60 days) |
| `get_solar_elevation_angle(location, time, date?, tz?, alt?)` | Solar elevation / azimuth | Astronomy: solar elevation angle |
| `get_weather_alerts(location, local_time?)` | Active official warning list | Weather warnings (most countries worldwide) |
| `get_weather_report(location)` | Ready-to-send Markdown (today's overview + 3-day forecast + tips) | Push / notification scenarios |

`location` accepts a city name, a LocationID, or `"lon,lat"` (e.g. `"116.41,39.92"`). Weather tools query by lat-lon via the v1 API (1 km resolution, global coverage); `get_weather_report` is generated from v1 daily forecast data. Only life indices still use the v7 endpoint (`/v7/indices`, no v1 equivalent).

Endpoint-to-docs mapping lives in [`docs/`](docs/). Adding a new API = one method in `client.py` + one `@mcp.tool()` in `server.py`.

## Configuration

**Environment variables only** (12-factor); no config file. CLI flags (`--transport/--host/--port`) only control how the server runs. A missing required variable fails at startup, naming exactly what's missing.

| Variable | Description |
| --- | --- |
| `QWEATHER_API_HOST` | Your dedicated API host, e.g. `your-host.re.qweatherapi.com` (required) |
| `QWEATHER_PROJECT_ID` | Project ID, JWT `sub` (required) |
| `QWEATHER_CREDENTIAL_ID` | Credential ID, JWT `kid` (required) |
| `QWEATHER_PRIVATE_KEY_PATH` | Ed25519 private key path, default `~/.ssh/ed25519-private.pem` |

The private key never leaves the filesystem: no client config file, no LLM context. Only the host and the two non-secret IDs live in client configs.

## Run

Install as a global tool:

```bash
uv tool install .
```

```bash
# stdio (default; local clients spawn it)
qweather-mcp

# streamable-http (deploy as a shared service; clients just point at a URL)
qweather-mcp --transport streamable-http --host 0.0.0.0 --port 8111
```

Reinstall after code changes: `uv tool install --force .`. For development, `uv tool install -e .` gives you edit-in-place behavior.

For quick development runs of streamable-http:

```bash
uv run qweather-mcp --transport streamable-http   # 127.0.0.1:8111/mcp by default
```

## Client integration

**Claude Code** (`.mcp.json`):

```json
{
  "mcpServers": {
    "qweather": {
      "command": "/Users/you/.local/bin/qweather-mcp",
      "env": {
        "QWEATHER_API_HOST": "<your dedicated API host>",
        "QWEATHER_PROJECT_ID": "<project ID>",
        "QWEATHER_CREDENTIAL_ID": "<credential ID>"
      }
    }
  }
}
```

**Other MCP clients** (Claude Desktop, Gemini, agents, …): the same `command` + the three env vars above in each client's MCP config.

**Shared-service mode**: run `qweather-mcp --transport streamable-http --host 0.0.0.0 --port 8111`, then register `http://127.0.0.1:8111/mcp` in any client that speaks streamable-http (e.g. LangChain/LangGraph `load_mcp_tools`). Network isolation (cluster-internal only) is recommended for deployments.

**Container deployment**: `uv tool install .` (or pip install) inside the image, run `qweather-mcp --transport streamable-http`; config all via container env, mount the private key as a secret and point `QWEATHER_PRIVATE_KEY_PATH` at it.

## License

[MIT](LICENSE)
