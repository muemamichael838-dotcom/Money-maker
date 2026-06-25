# Deployment Fix: Money Maker 🤑 (v1.2) - ECONNREFUSED Resolving

## Problem
Users reported a `proxy_error: ECONNREFUSED 127.0.0.1:9119` after logging in.
Diagnosis:
1. **Startup Lag**: The heavy Python-based dashboard takes 10-30 seconds to fully initialize and bind to its port.
2. **Binary Pathing**: The previous `start.sh` relied on `market-insights` which might not have been correctly linked in all environments.

## Solution
- **Absolute Targeting**: Updated `start.sh` to explicitly search for and use absolute paths for the `hermes` binary (`/opt/hermes/.venv/bin/hermes`).
- **Wait-for-Service UI**: Modified `health-server.js` to catch `ECONNREFUSED`. Instead of a JSON error, it now serves a professional "Engine Warming Up" HTML page with an auto-refresh script. This keeps the user engaged while the dashboard starts.
- **Internal Networking**: Standardized all internal service hosts to `0.0.0.0` or `127.0.0.1` consistently to avoid bridge networking issues on Render.

## UX Improvement
The "Starting Up" page provides immediate visual feedback that the system is working, reducing perceived "brokenness" during the initial container boot.
