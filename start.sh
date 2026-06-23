#!/bin/bash
set -euo pipefail

# Re-branding
echo "Starting MarketInsights-AI Ultimate..."

export MARKET_INSIGHTS_HOME="${MARKET_INSIGHTS_HOME:-/opt/data}"
export MARKET_INSIGHTS_APP_DIR="${MARKET_INSIGHTS_APP_DIR:-/opt/market-insights}"
export APP_DIR="${MARKET_INSIGHTS_APP_DIR}"
export PORT="${PORT:-7860}" # HF Default
export GATEWAY_API_PORT="${GATEWAY_API_PORT:-8642}"
export DASHBOARD_PORT="${DASHBOARD_PORT:-9119}"

mkdir -p "${MARKET_INSIGHTS_HOME}/workspace" "${MARKET_INSIGHTS_HOME}/logs"

# Start Health Server (Entry point for HF)
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

# Initial background services
start_api_proxy
start_cron_manager
start_dashboard

# Set Hermes to use our local proxy
export OPENAI_BASE_URL="http://127.0.0.1:8000/v1"

# Gateway loop
while true; do
  echo "Launching MarketInsights-AI AI Gateway..."
  (market-insights gateway run --port "$GATEWAY_API_PORT" 2>&1 | tee -a "$MARKET_INSIGHTS_HOME/logs/gateway.log") &
  GATEWAY_PID=$!
  wait "$GATEWAY_PID" || echo "Gateway exited."
  sleep 5
done
