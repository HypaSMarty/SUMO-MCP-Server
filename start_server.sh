#!/bin/bash
# SUMO-MCP Server Startup Script for Linux/macOS/MSYS
# 说明：
# - SUMO 需已安装
# - 推荐：在系统环境变量中设置 SUMO_HOME，并确保 $SUMO_HOME/bin 在 PATH 中
# - 若未设置 SUMO_HOME，本脚本将仅依赖 PATH 中的 `sumo`/`netgenerate` 等二进制

if [ -n "${SUMO_HOME:-}" ]; then
  export PATH="$SUMO_HOME/bin:$PATH"
fi

if ! command -v sumo &> /dev/null; then
  if [ -z "${SUMO_HOME:-}" ]; then
    echo "Error: SUMO not found. Please install SUMO or set SUMO_HOME." >&2
  else
    echo "Error: \`sumo\` not found in PATH after applying SUMO_HOME=$SUMO_HOME (expected $SUMO_HOME/bin)." >&2
  fi
  exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 启动 MCP 服务器
python "$SCRIPT_DIR/src/server.py"
