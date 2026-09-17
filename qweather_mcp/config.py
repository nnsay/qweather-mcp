"""配置: 一律环境变量 (12-factor), 没有配置文件; 缺失即刻失败并指明缺哪个。

QWEATHER_API_HOST          专属 API host, 如 your-host.re.qweatherapi.com (必填)
QWEATHER_PROJECT_ID        项目 ID (JWT sub, 必填)
QWEATHER_CREDENTIAL_ID     凭据 ID (JWT kid, 必填)
QWEATHER_PRIVATE_KEY_PATH  Ed25519 私钥路径 (默认 ~/.ssh/ed25519-private.pem)
"""

import os
from dataclasses import dataclass
from pathlib import Path

# 私钥留在 ~/.ssh 即可: skill/agent 有沙箱规则读不到它, 而 MCP server 是
# 无沙箱的独立进程, 可以直接读 —— 凭证对 LLM 和沙箱内代码保持不可见。
DEFAULT_PRIVATE_KEY_PATH = Path.home() / ".ssh" / "ed25519-private.pem"


class QWeatherConfigError(RuntimeError):
    """配置缺失/不合法。库函数抛异常 (不用 SystemExit), 由入口决定如何退出。"""


@dataclass(frozen=True)
class QWeatherConfig:
    api_host: str
    project_id: str  # JWT sub
    credential_id: str  # JWT kid
    private_key_path: Path

    @property
    def api_base_url(self) -> str:
        return f"https://{self.api_host}"


def load_config() -> QWeatherConfig:
    missing = [
        name
        for name in (
            "QWEATHER_API_HOST",
            "QWEATHER_PROJECT_ID",
            "QWEATHER_CREDENTIAL_ID",
        )
        if not os.environ.get(name)
    ]
    if missing:
        raise QWeatherConfigError(f"缺少环境变量: {', '.join(missing)}")

    private_key = Path(
        os.environ.get("QWEATHER_PRIVATE_KEY_PATH", DEFAULT_PRIVATE_KEY_PATH)
    ).expanduser()
    if not private_key.is_file():
        raise QWeatherConfigError(
            f"私钥文件不存在: {private_key} (可用 QWEATHER_PRIVATE_KEY_PATH 指定)"
        )

    return QWeatherConfig(
        api_host=os.environ["QWEATHER_API_HOST"],
        project_id=os.environ["QWEATHER_PROJECT_ID"],
        credential_id=os.environ["QWEATHER_CREDENTIAL_ID"],
        private_key_path=private_key,
    )
