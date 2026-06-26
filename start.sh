#!/bin/bash
# Money Maker Agent 🤑 - Security Bypass Build v11.0
set -u

echo "--- MONEY MAKER SECURITY BYPASS BOOT ---"

export MONEY_MAKER_HOME="${MONEY_MAKER_HOME:-/opt/data}"
export HERMES_HOME="$MONEY_MAKER_HOME"
export APP_DIR="/app"
export HERMES_WEB_DIST="${APP_DIR}/money-maker-ui"
mkdir -p "${MONEY_MAKER_HOME}/logs"

# SECURITY OVERRIDES
export ALLOWED_HOSTS="*"
export DASHBOARD_ALLOWED_HOSTS="*"
export CSRF_TRUSTED_ORIGINS="*"
export HOST="127.0.0.1"

# Ensure log files exist
touch "${MONEY_MAKER_HOME}/logs/dashboard.log"

# 1. Start Health/Proxy Server (Binds to $PORT)
node "${APP_DIR}/health-server.js" 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/health-server.log" &

# 2. Identify Python Environment
PYTHON_BIN="/opt/hermes/.venv/bin/python"
[ ! -f "$PYTHON_BIN" ] && PYTHON_BIN=$(which python3)

# 3. Start Multi-Layer API Proxy
$PYTHON_BIN "${APP_DIR}/api_proxy.py" 2>&1 | tee -a "$MONEY_MAKER_HOME/logs/api_proxy.log" &

# 4. Launch Money Maker Control Center
echo "Launching Money Maker Control Center..."
{
    $PYTHON_BIN -m hermes_cli.main dashboard --host 127.0.0.1 --port 9119 --insecure
} >> "$MONEY_MAKER_HOME/logs/dashboard.log" 2>&1 &

# 5. Support Services
$PYTHON_BIN "${APP_DIR}/cron_manager.py" > "$MONEY_MAKER_HOME/logs/cron_manager.log" 2>&1 &
$PYTHON_BIN "${APP_DIR}/render_keepalive.py" > "$MONEY_MAKER_HOME/logs/keepalive.log" 2>&1 &

# 6. AI Gateway Loop
export API_SERVER_PORT=8642
export OPENAI_BASE_URL="http://127.0.0.1:8000/v1"

while true; do
  echo "Starting Money Maker AI Gateway..."
  $PYTHON_BIN -m hermes_cli.main gateway run >> "$MONEY_MAKER_HOME/logs/gateway.log" 2>&1
  echo "Gateway exited, restarting in 20s..."
  sleep 20
done
