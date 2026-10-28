# qweather-mcp 生产镜像: 构建 (uv build, 见 nx dockerize → build) 的 wheel → 轻量运行时。
# 运行: streamable-http, agent-api 经 MCP_SERVERS 指 http://qweather-mcp:8111/mcp
FROM docker.m.daocloud.io/library/python:3.12-slim-bookworm
COPY dist/nnsay_qweather_mcp-*.whl /tmp/
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ /tmp/nnsay_qweather_mcp-*.whl \
    && rm /tmp/nnsay_qweather_mcp-*.whl

# 非 root 运行 (与 agent-api 同一安全基线); /run/secrets 里的 key 默认 0444, 仍可读。
# WORKDIR 给到用户家目录, 避免进程若写 cwd 撞上根目录只读权限。
RUN useradd -m -u 1000 qweather
USER qweather
WORKDIR /home/qweather

ENTRYPOINT ["qweather-mcp", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8111"]
