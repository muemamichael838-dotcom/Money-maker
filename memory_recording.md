# Deployment Fix: Money Maker 🤑 (v2.0) - Host Header Resolution

## Problem
The dashboard engine (Tornado/FastAPI) was rejecting requests with `{"detail":"Invalid Host header"}` because the external hostname (e.g., `money-maker.onrender.com`) did not match the internal binding (`127.0.0.1`).

## Solution
- **Host Header Masking**: Updated `health-server.js` to rewrite the `Host` and `Origin` headers to `127.0.0.1:9119` before sending the request to the dashboard. This makes the dashboard believe it is being accessed directly from the local machine.
- **Proxy Transparency**: Added `X-Forwarded-Host` and `X-Forwarded-Proto` headers to preserve the original client information for logging and security within the agent.
- **Security Wildcards**: Set `ALLOWED_HOSTS=*` and `CSRF_TRUSTED_ORIGINS=*` in `start.sh` to explicitly tell the engine to trust the proxied traffic.

## UX Improvement
The dashboard now loads correctly after login without security-related 400 errors.
