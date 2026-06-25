#!/bin/bash
# Money Maker Agent 🤑 - Ultimate Survival Script v1.9
set -u

echo "--- MONEY MAKER SURVIVAL BOOT ---"

export MONEY_MAKER_HOME="${MONEY_MAKER_HOME:-/opt/data}"
export APP_DIR="/opt/market-insights"
mkdir -p "${MONEY_MAKER_HOME}/logs"

# Ensure log files exist
touch "${MONEY_MAKER_HOME}/logs/dashboard.log"

# 1. Start Health/Proxy Server FIRST (satisfies Render port check)
echo "Launching Health & Diagnostics Proxy (Port ${PORT:-10000})..."
node "${APP_DIR}/health-server.js" 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/health-server.log" &

# 2. Memory Info
echo "System Memory Status:" >> "$MONEY_MAKER_HOME/logs/dashboard.log"
free -m >> "$MONEY_MAKER_HOME/logs/dashboard.log"

# 3. Identify/Repair Python Environment
PYTHON_BIN="/opt/hermes/.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN=$(which python3)
fi

echo "Using Python: $PYTHON_BIN" >> "$MONEY_MAKER_HOME/logs/dashboard.log"

# 4. Critical: Ensure hermes-agent is installed
if ! $PYTHON_BIN -m hermes --help > /dev/null 2>&1; then
    echo "Engine not found. Attempting emergency install..." >> "$MONEY_MAKER_HOME/logs/dashboard.log"
    $PYTHON_BIN -m pip install hermes-agent litellm fastapi uvicorn requests beautifulsoup4 schedule apify-client --no-cache-dir >> "$MONEY_MAKER_HOME/logs/dashboard.log" 2>&1
fi

# 5. Find the hermes binary
HERMES_BIN="/opt/hermes/.venv/bin/hermes"
if [ ! -f "$HERMES_BIN" ]; then
    HERMES_BIN=$(which hermes || echo "$PYTHON_BIN -m hermes")
fi

# 6. Start Multi-Layer API Proxy (Port 8000)
echo "Starting Multi-Key LLM Proxy..."
$PYTHON_BIN "${APP_DIR}/api_proxy.py" 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/api_proxy.log" &

# 7. Start Dashboard (Port 9119)
# Use 127.0.0.1 to keep it internal for the proxy
echo "Launching Money Maker Dashboard..."
{
    echo "Attempting dashboard launch..."
    $HERMES_BIN dashboard --host 127.0.0.1 --port 9119 --insecure || \
    $PYTHON_BIN -m hermes dashboard --host 127.0.0.1 --port 9119 --insecure || \
    $PYTHON_BIN -m hermes_agent dashboard --host 127.0.0.1 --port 9119 --insecure
} >> "$MONEY_MAKER_HOME/logs/dashboard.log" 2>&1 &

# 8. AI Gateway Loop
export API_SERVER_PORT=8642
export OPENAI_BASE_URL="http://127.0.0.1:8000/v1"

while true; do
  echo "Monitoring AI Gateway..."
  $HERMES_BIN gateway run >> "$MONEY_MAKER_HOME/logs/gateway.log" 2>&1 || \
  $PYTHON_BIN -m hermes gateway run >> "$MONEY_MAKER_HOME/logs/gateway.log" 2>&1 || \
  echo "Gateway exited."
  sleep 20
done
