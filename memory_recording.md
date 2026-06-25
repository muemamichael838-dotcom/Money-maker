# Deployment Fix: Money Maker 🤑 (v1.3) - Dashboard Port Stability

## Problem
The error `connect ECONNREFUSED 127.0.0.1:9119` persisted because the dashboard service was either crashing on start or failing to bind to the port using the primary command.

## Solution
- **Multi-Phase Startup**: Updated `start.sh` to attempt three different ways of launching the dashboard:
    1. Using the absolute `market-insights` binary.
    2. Using the virtual environment's `hermes` binary.
    3. Using the Python module directly (`python -m hermes.dashboard`).
- **Emergency Diagnostics**: Added a `/api/logs` endpoint to the health server. This allows users to view the last 50 lines of the `dashboard.log` file directly in their browser if the dashboard fails to load.
- **Networking Precision**: Standardized all internal service calls to `127.0.0.1` to eliminate any DNS or hostname resolution overhead during container boot.

## UX Improvement
The system now provides a clear path for debugging (`/api/logs`) if the "Engine Warming Up" screen persists for more than 60 seconds.
