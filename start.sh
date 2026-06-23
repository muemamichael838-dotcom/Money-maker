#!/bin/bash
set -euo pipefail

# Money Maker🤑 - AI Agent Startup Script
# Based on HuggingMes/Hermes Agent

export HERMES_HOME="${HERMES_HOME:-/opt/data}"
export MONEY_MAKER_APP_DIR="${MONEY_MAKER_APP_DIR:-/opt/money-maker}"
export APP_DIR="${MONEY_MAKER_APP_DIR}"
export STARTUP_FILE="${HERMES_HOME}/workspace/startup.sh"
export GATEWAY_API_PORT="${GATEWAY_API_PORT:-7860}"
export DASHBOARD_PORT="${DASHBOARD_PORT:-7861}"
export JUPYTER_PORT="${JUPYTER_PORT:-8888}"

# Ensure directories exist
mkdir -p "${HERMES_HOME}/workspace" "${HERMES_HOME}/logs" "${HERMES_HOME}/.local/bin"

# Help functions
start_api_proxy() {
  if [ -n "${API_PROXY_PID:-}" ] && kill -0 "$API_PROXY_PID" 2>/dev/null; then return 0; fi
  echo "Launching Multi-Layer API Proxy..."
  /opt/hermes/.venv/bin/python ${MONEY_MAKER_APP_DIR}/api_proxy.py &
  API_PROXY_PID=$!
}

start_cron_manager() {
  if [ -n "${CRON_MANAGER_PID:-}" ] && kill -0 "$CRON_MANAGER_PID" 2>/dev/null; then return 0; fi
  echo "Launching Cron Manager..."
  /opt/hermes/.venv/bin/python ${MONEY_MAKER_APP_DIR}/cron_manager.py &
  CRON_MANAGER_PID=$!
}

start_dashboard_once() {
  if [ -n "${DASHBOARD_PID:-}" ] && kill -0 "$DASHBOARD_PID" 2>/dev/null; then return 0; fi
  echo "Launching Money Maker dashboard on 127.0.0.1:${DASHBOARD_PORT}..."
  (hermes dashboard --host 127.0.0.1 --insecure 2>&1 | tee -a "$HERMES_HOME/logs/dashboard.log") &
  DASHBOARD_PID=$!
}

start_jupyter() {
  if [ "${DEV_MODE:-true}" == "false" ]; then return 0; fi
  if [ -n "${JUPYTER_PID:-}" ] && kill -0 "$JUPYTER_PID" 2>/dev/null; then return 0; fi
  echo "Launching JupyterLab terminal..."
  (jupyter lab --ip=127.0.0.1 --port=${JUPYTER_PORT} --no-browser --NotebookApp.token="${GATEWAY_TOKEN:-}" --NotebookApp.password="" 2>&1 | tee -a "$HERMES_HOME/logs/jupyter.log") &
  JUPYTER_PID=$!
}

start_background_sync_once() {
  [ -n "${HF_TOKEN:-}" ] || return 0
  if [ -n "${SYNC_LOOP_PID:-}" ] && kill -0 "$SYNC_LOOP_PID" 2>/dev/null; then return 0; fi
  python3 -u "$APP_DIR/hermes-sync.py" loop &
  SYNC_LOOP_PID=$!
}

# Main Execution
echo "Starting Money Maker🤑 Services..."

start_api_proxy
start_cron_manager
start_dashboard_once
start_jupyter
start_background_sync_once

# Gateway restart loop
while true; do
  echo "Launching Hermes gateway..."
  (hermes gateway run 2>&1 | tee -a "$HERMES_HOME/logs/gateway.log") &
  GATEWAY_PID=$!

  wait "$GATEWAY_PID" || echo "Gateway exited."

  # Sync state on exit
  if [ -n "${HF_TOKEN:-}" ]; then
    python3 "$APP_DIR/hermes-sync.py" sync-once || true
    /opt/hermes/.venv/bin/python ${MONEY_MAKER_APP_DIR}/sync_helper.py || true
  fi

  echo "Restarting gateway in 5s..."
  sleep 5

  # Health checks for sidecars
  start_api_proxy
  start_cron_manager
  start_dashboard_once
  start_jupyter
done
