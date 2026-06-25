# Bug Fix: Money Maker 🤑 - Proxy Redirect Crash

## Issue
The health server was intermittently returning 502 errors on Render.
Diagnosis revealed a logic error in the root path (`/`) handler:
```javascript
if (path === "/") {
  // ...
  res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
  redirect(res, `${APP_BASE}/`); // This calls writeHead(302)
  return;
}
```
This caused a "Cannot set headers after they are sent to the client" error in Node.js, crashing the request handler and leading to a Bad Gateway (502).

## Solution
1. Removed the redundant `res.writeHead(200)` call before `redirect()`.
2. Wrapped the entire request handler in a `try/catch` block to ensure the server stays alive and logs errors properly.
3. Enhanced logging in `start.sh` to capture health server output to disk.

## Learning
Always ensure that only one "terminal" response method (like `redirect`, `end`, or `writeHead`) is called per request path. Wrapping handlers in `try/catch` is essential for production-grade health servers to prevent single-request failures from cascading into service downtime.
