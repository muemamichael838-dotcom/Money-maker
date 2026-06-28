#!/bin/bash
# Money Maker 🤑 - 24/7 Neural Orchestrator
set -e

echo "--- [SYSTEM] Money Maker Engine Ignition ---"

# 1. Environment Setup
export MONEY_MAKER_HOME="${MONEY_MAKER_HOME:-/opt/data}"
mkdir -p "${MONEY_MAKER_HOME}/logs"
touch "${MONEY_MAKER_HOME}/agent.log"

PYTHON_BIN="/opt/hermes/.venv/bin/python"
[ ! -f "$PYTHON_BIN" ] && PYTHON_BIN=$(which python3)

# Ensure the UI directory exists
mkdir -p /app/money-maker-ui

# 2. Launch Supporting Neural Probes (Background)
echo "--- [BOOT] Launching Proxy Layer ---"
$PYTHON_BIN /app/api_proxy.py > "${MONEY_MAKER_HOME}/logs/proxy.log" 2>&1 &

echo "--- [BOOT] Launching Chat Bridge ---"
$PYTHON_BIN /app/chat_bridge.py > "${MONEY_MAKER_HOME}/logs/bridge.log" 2>&1 &

echo "--- [BOOT] Launching Autonomous Crons ---"
$PYTHON_BIN /app/cron_manager.py > "${MONEY_MAKER_HOME}/logs/cron.log" 2>&1 &

# 3. Launch Root Dashboard (Hermes CLI Dashboard)
echo "--- [BOOT] Launching Core Command Center (Port 9119) ---"
$PYTHON_BIN -m hermes_cli.main dashboard --host 127.0.0.1 --port 9119 --insecure > "${MONEY_MAKER_HOME}/logs/dashboard.log" 2>&1 &

# 4. Launch Edge Health & Router (Foreground, Port $PORT)
echo "--- [BOOT] Edge Router Deployed. System Online. ---"
node /app/health-server.js
