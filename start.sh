#!/bin/bash
set -euo pipefail

echo "Starting MarketInsights-AI Ultimate..."

export MARKET_INSIGHTS_HOME="${MARKET_INSIGHTS_HOME:-/opt/data}"
export MARKET_INSIGHTS_APP_DIR="${MARKET_INSIGHTS_APP_DIR:-/opt/market-insights}"
export APP_DIR="${MARKET_INSIGHTS_APP_DIR}"
export PORT="${PORT:-10000}"
export GATEWAY_API_PORT="${GATEWAY_API_PORT:-8642}"
export DASHBOARD_PORT="${DASHBOARD_PORT:-9119}"
export JUPYTER_PORT="${JUPYTER_PORT:-8888}"

mkdir -p "${MARKET_INSIGHTS_HOME}/workspace" "${MARKET_INSIGHTS_HOME}/logs" "${MARKET_INSIGHTS_HOME}/.local/bin"

# Start Health Server
node "${APP_DIR}/health-server.js" &
HEALTH_PID=$!

start_api_proxy() {
  echo "Launching Multi-Layer API Proxy (Port 8000)..."
  /opt/hermes/.venv/bin/python "${APP_DIR}/api_proxy.py" &
}

start_cron_manager() {
  echo "Launching Autonomous Cron Manager..."
  /opt/hermes/.venv/bin/python "${APP_DIR}/cron_manager.py" &
}

start_dashboard() {
  echo "Launching Pro Dashboard..."
  (market-insights dashboard --host 127.0.0.1 --port "$DASHBOARD_PORT" --insecure 2>&1 | tee -a "$MARKET_INSIGHTS_HOME/logs/dashboard.log") &
}

start_jupyter() {
  if [ "${DEV_MODE:-true}" == "false" ]; then return 0; fi
  echo "Launching Terminal Interface (JupyterLab)..."
  (/opt/hermes/.venv/bin/python -m jupyterlab --ip=127.0.0.1 --port=${JUPYTER_PORT} --no-browser --NotebookApp.token="${GATEWAY_TOKEN:-}" --NotebookApp.password="" 2>&1 | tee -a "$MARKET_INSIGHTS_HOME/logs/jupyter.log") &
  JUPYTER_PID=$!
}

start_keepalive() {
  echo "Launching Keep-Alive Service..."
  /opt/hermes/.venv/bin/python "${APP_DIR}/render_keepalive.py" &
}

start_background_sync_once() {
  if [ -z "${HF_TOKEN:-}" ]; then
    echo "Warning: HF_TOKEN not set. Persistence sync disabled."
    return 0
  fi
  echo "Launching HF Dataset Persistence Sync..."
  python3 -u "${APP_DIR}/hermes-sync.py" loop &
}

# Initial background services
start_api_proxy
start_cron_manager
start_dashboard
start_jupyter
start_keepalive
start_background_sync_once

export OPENAI_BASE_URL="http://127.0.0.1:8000/v1"

while true; do
  echo "Launching MarketInsights-AI AI Gateway..."
  (market-insights gateway run --port "$GATEWAY_API_PORT" 2>&1 | tee -a "$MARKET_INSIGHTS_HOME/logs/gateway.log") &
  GATEWAY_PID=$!

  wait "$GATEWAY_PID" || echo "Gateway exited."

  # Final sync before possible restart/shutdown
  if [ -n "${HF_TOKEN:-}" ]; then
    python3 "${APP_DIR}/hermes-sync.py" sync-once || true
    /opt/hermes/.venv/bin/python "${APP_DIR}/sync_helper.py" || true
  fi

  sleep 5
done
