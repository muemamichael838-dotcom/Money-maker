#!/bin/bash
set -euo pipefail

echo "Starting Money Maker Agent 🤑..."

# Use current dir if /opt/data is not writable (for local testing)
if [ -w "/opt/data" ]; then
    export MONEY_MAKER_HOME="/opt/data"
else
    export MONEY_MAKER_HOME="${HOME}/money_maker_data"
fi

export APP_DIR="/app"
export PORT="${PORT:-10000}"
export GATEWAY_API_PORT="${GATEWAY_API_PORT:-8642}"
export DASHBOARD_PORT="${DASHBOARD_PORT:-9119}"
export JUPYTER_PORT="${JUPYTER_PORT:-8888}"

# Detection of Python environment
if [ -f "/opt/hermes/.venv/bin/python" ]; then
    PYTHON_BIN="/opt/hermes/.venv/bin/python"
    HERMES_BIN="/usr/local/bin/market-insights"
else
    PYTHON_BIN=$(which python3)
    HERMES_BIN=$(which hermes || echo "market-insights")
fi

mkdir -p "${MONEY_MAKER_HOME}/workspace" "${MONEY_MAKER_HOME}/logs" "${MONEY_MAKER_HOME}/.local/bin"

# Rebrand health server output
node "${APP_DIR}/health-server.js" &
HEALTH_PID=$!

start_api_proxy() {
  echo "Launching Multi-Layer API Proxy (Port 8000)..."
  $PYTHON_BIN "${APP_DIR}/api_proxy.py" &
}

start_cron_manager() {
  echo "Launching Autonomous Cron Manager..."
  $PYTHON_BIN "${APP_DIR}/cron_manager.py" &
}

start_dashboard() {
  echo "Launching Money Maker Pro Dashboard..."
  (market-insights dashboard --host 0.0.0.0 --port "$DASHBOARD_PORT" --insecure 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/dashboard.log") &
}

start_jupyter() {
  if [ "${DEV_MODE:-true}" == "false" ]; then return 0; fi
  echo "Launching Root Terminal (JupyterLab)..."
  ($PYTHON_BIN -m jupyterlab --ip=0.0.0.0 --port=${JUPYTER_PORT} --no-browser --NotebookApp.token="${GATEWAY_TOKEN:-}" --NotebookApp.password="" --allow-root 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/jupyter.log") &
}

start_keepalive() {
  echo "Launching 24/7 Keep-Alive Service..."
  $PYTHON_BIN "${APP_DIR}/render_keepalive.py" &
}

# Background services
start_api_proxy
start_cron_manager
start_dashboard
start_jupyter
start_keepalive

export OPENAI_BASE_URL="http://127.0.0.1:8000/v1"

while true; do
  echo "Launching Money Maker AI Gateway..."
  export API_SERVER_PORT="$GATEWAY_API_PORT"
  (market-insights gateway run 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/gateway.log") &
  GATEWAY_PID=$!

  wait "$GATEWAY_PID" || echo "Gateway exited. Retrying with another API key if configured..."

  sleep 5
done
