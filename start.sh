#!/bin/bash
set -euo pipefail

export HERMES_HOME="${HERMES_HOME:-/opt/data}"
export MONEY_MAKER_APP_DIR="${MONEY_MAKER_APP_DIR:-/opt/money-maker}"
export APP_DIR="${MONEY_MAKER_APP_DIR}"

mkdir -p "${HERMES_HOME}/workspace" "${HERMES_HOME}/logs"

start_api_proxy() {
  echo "Launching API Proxy..."
  /opt/hermes/.venv/bin/python ${MONEY_MAKER_APP_DIR}/api_proxy.py &
}

start_cron_manager() {
  echo "Launching Cron Manager..."
  /opt/hermes/.venv/bin/python ${MONEY_MAKER_APP_DIR}/cron_manager.py &
}

start_dashboard() {
  echo "Launching Dashboard..."
  (hermes dashboard --host 127.0.0.1 --insecure 2>&1 | tee -a "$HERMES_HOME/logs/dashboard.log") &
}

# Start all components
start_api_proxy
start_cron_manager
start_dashboard

# Gateway loop
while true; do
  echo "Launching Hermes gateway..."
  (hermes gateway run 2>&1 | tee -a "$HERMES_HOME/logs/gateway.log") &
  GATEWAY_PID=$!
  wait "$GATEWAY_PID" || echo "Gateway exited."
  sleep 5
done
