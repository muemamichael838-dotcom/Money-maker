#!/bin/bash
set -euo pipefail

echo "Starting Money Maker Agent 🤑 (v1.4)..."

export MONEY_MAKER_HOME="${MONEY_MAKER_HOME:-/opt/data}"
export APP_DIR="/opt/market-insights"
cd "$APP_DIR"

export PORT="${PORT:-10000}"
export GATEWAY_API_PORT="${GATEWAY_API_PORT:-8642}"
export DASHBOARD_PORT="${DASHBOARD_PORT:-9119}"
export JUPYTER_PORT="${JUPYTER_PORT:-8888}"

# Find Python
PYTHON_BIN="/opt/hermes/.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then PYTHON_BIN=$(which python3); fi

# Find Hermes
HERMES_BIN="/usr/local/bin/market-insights"
if [ ! -f "$HERMES_BIN" ]; then HERMES_BIN="/opt/hermes/.venv/bin/hermes"; fi
if [ ! -f "$HERMES_BIN" ]; then HERMES_BIN=$(which market-insights || which hermes || echo "hermes"); fi

mkdir -p "${MONEY_MAKER_HOME}/workspace" "${MONEY_MAKER_HOME}/logs" "${MONEY_MAKER_HOME}/.local/bin"

echo "Launching Primary Health Server on 0.0.0.0:$PORT..."
node "${APP_DIR}/health-server.js" 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/health-server.log" &

start_api_proxy() {
  echo "Launching Multi-Layer API Proxy (Port 8000)..."
  $PYTHON_BIN "${APP_DIR}/api_proxy.py" 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/api_proxy.log" &
}

start_cron_manager() {
  echo "Launching Autonomous Cron Manager..."
  $PYTHON_BIN "${APP_DIR}/cron_manager.py" 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/cron_manager.log" &
}

start_dashboard() {
  echo "Attempting to launch Money Maker Dashboard on 0.0.0.0:$DASHBOARD_PORT..."
  # Try binary first, then python module directly
  ($HERMES_BIN dashboard --host 0.0.0.0 --port "$DASHBOARD_PORT" --insecure 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/dashboard.log") || \
  ($PYTHON_BIN -m hermes.dashboard --host 0.0.0.0 --port "$DASHBOARD_PORT" --insecure 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/dashboard.log") || \
  ($PYTHON_BIN -m hermes dashboard --host 0.0.0.0 --port "$DASHBOARD_PORT" --insecure 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/dashboard.log") || \
  echo "CRITICAL: Dashboard failed to start using all methods." | tee -a "$MONEY_MAKER_HOME/logs/dashboard.log" &
}

start_jupyter() {
  if [ "${DEV_MODE:-true}" == "false" ]; then return 0; fi
  echo "Launching Root Terminal (JupyterLab)..."
  ($PYTHON_BIN -m jupyterlab --ip=0.0.0.0 --port=${JUPYTER_PORT} --no-browser --NotebookApp.token="${GATEWAY_TOKEN:-}" --NotebookApp.password="" --allow-root 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/jupyter.log") &
}

start_keepalive() {
  echo "Launching 24/7 Keep-Alive Service..."
  $PYTHON_BIN "${APP_DIR}/render_keepalive.py" 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/keepalive.log" &
}

start_api_proxy
start_cron_manager
start_dashboard
start_jupyter
start_keepalive

export OPENAI_BASE_URL="http://127.0.0.1:8000/v1"

while true; do
  echo "Launching Money Maker AI Gateway..."
  export API_SERVER_PORT="$GATEWAY_API_PORT"
  $HERMES_BIN gateway run 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/gateway.log" || \
  $PYTHON_BIN -m hermes.gateway run 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/gateway.log" || \
  echo "Gateway exited."
  sleep 5
done
