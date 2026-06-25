"use strict";

const http = require("http");
const https = require("https");
const fs = require("fs");
const net = require("net");
const crypto = require("crypto");

const PORT = process.env.PORT || 10000;
const GATEWAY_HOST = "127.0.0.1";
const GATEWAY_PORT = process.env.GATEWAY_API_PORT || 8642;
const DASHBOARD_PORT = process.env.DASHBOARD_PORT || 9119;
const JUPYTER_PORT = process.env.JUPYTER_PORT || 8888;
const TELEGRAM_WEBHOOK_PORT = 8000;

const API_SERVER_KEY = process.env.GATEWAY_TOKEN || "";
const APP_BASE = "/app";
const TERMINAL_BASE = "/terminal";
const LOGIN_PATH = "/login";

const SPACE_ID = process.env.SPACE_ID || "";
const HF_SPACE_URL = SPACE_ID ? `https://huggingface.co/spaces/${SPACE_ID}` : "";

let SPACE_IS_PRIVATE = !!SPACE_ID;
let _privacyDetectionDone = false;

// Helpers
const log = (msg) => console.log(`[${new Date().toISOString()}] [health-server] ${msg}`);
const err = (msg, error) => console.error(`[${new Date().toISOString()}] [health-server] ERROR: ${msg}`, error || "");

const privacyDetectionReady = (async () => {
  if (!SPACE_ID) {
    _privacyDetectionDone = true;
    return;
  }
  log(`Detecting privacy for Space: ${SPACE_ID}`);
  const apiUrl = `https://huggingface.co/api/spaces/${SPACE_ID}`;
  try {
    const fetch = (url) =>
      new Promise((resolve, reject) => {
        https.get(
          url,
          { headers: { "User-Agent": "Money Maker 🤑/health-server" } },
          (res) => {
            let data = "";
            res.on("data", (chunk) => (data += chunk));
            res.on("end", () => resolve({ status: res.statusCode, data }));
          },
        ).on("error", reject);
      });

    const { status, data } = await fetch(apiUrl);
    if (status === 200) {
      const json = JSON.parse(data);
      SPACE_IS_PRIVATE = json.private === true;
      log(`Space privacy detected: ${SPACE_IS_PRIVATE ? "PRIVATE" : "PUBLIC"}`);
    }
  } catch (e) {
    err("Privacy detection failed", e);
  } finally {
    _privacyDetectionDone = true;
  }
})();

function isAuthorized(req) {
  if (!API_SERVER_KEY) return true;
  const cookieHeader = req.headers.cookie || "";
  const cookies = Object.fromEntries(
    cookieHeader.split(";").map((c) => c.trim().split("=")),
  );
  if (cookies.token === API_SERVER_KEY) return true;
  const authHeader = req.headers.authorization || "";
  return authHeader === `Bearer ${API_SERVER_KEY}`;
}

function getBearerToken(req) {
  const auth = req.headers.authorization || "";
  if (auth.startsWith("Bearer ")) return auth.substring(7);
  return null;
}

function sendResponse(res, status, type, content) {
    if (res.headersSent) return;
    res.writeHead(status, {
        "Content-Type": type,
        "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate"
    });
    res.end(content);
}

function redirect(res, location, statusCode = 302) {
    if (res.headersSent) return;
    res.writeHead(statusCode, { "Location": location });
    res.end();
}

function wantsHtml(req) {
  return (req.headers.accept || "").includes("text/html");
}

function loginUrl(next) {
  return `${LOGIN_PATH}?next=${encodeURIComponent(next)}`;
}

async function handleLogin(req, res, parsed) {
  if (req.method === "POST") {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      const params = new URLSearchParams(body);
      const password = params.get("password");
      if (password === API_SERVER_KEY) {
        if (res.headersSent) return;
        res.writeHead(302, {
          location: params.get("next") || "/",
          "set-cookie": `token=${password}; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000`,
        });
        res.end();
      } else {
        sendResponse(res, 200, "text/html", renderLoginPage("Invalid password.", params.get("next")));
      }
    });
    return;
  }
  sendResponse(res, 200, "text/html", renderLoginPage("", parsed.searchParams.get("next")));
}

function renderLoginPage(error = "", next = "") {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Money Maker 🤑 - Login</title>
  <style>
    body { background: #0b0e14; color: #e1e1e1; font-family: sans-serif; display: flex; height: 100vh; margin: 0; align-items: center; justify-content: center; }
    .card { background: #1a1d23; padding: 2rem; border-radius: 8px; width: 320px; text-align: center; }
    h1 { color: #10a37f; }
    input { width: 100%; padding: 10px; margin: 15px 0; background: #2d3139; border: 1px solid #3e4451; color: white; border-radius: 4px; box-sizing: border-box; }
    button { background: #10a37f; color: white; border: none; padding: 10px; width: 100%; border-radius: 4px; cursor: pointer; }
    .error { color: #ff4b4b; margin-top: 10px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Money Maker 🤑</h1>
    <form method="POST">
      <input type="hidden" name="next" value="${next || ""}">
      <input type="password" name="password" placeholder="Gateway Token" required autofocus>
      <button type="submit">Unlock Dashboard</button>
      ${error ? `<div class="error">${error}</div>` : ""}
    </form>
  </div>
</body>
</html>`;
}

function canConnect(port) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    socket.setTimeout(300);
    socket.once("connect", () => {
      socket.destroy();
      resolve(true);
    });
    socket.once("timeout", () => {
      socket.destroy();
      resolve(false);
    });
    socket.once("error", () => {
      socket.destroy();
      resolve(false);
    });
    socket.connect(port, GATEWAY_HOST);
  });
}

async function statusPayload() {
  const [gateway, dashboard, jupyter] = await Promise.all([
    canConnect(GATEWAY_PORT),
    canConnect(DASHBOARD_PORT),
    canConnect(JUPYTER_PORT),
  ]);
  return {
    ok: gateway && dashboard,
    gateway,
    dashboard,
    jupyter,
    uptime: process.uptime(),
    private: SPACE_IS_PRIVATE,
  };
}

function proxyRequest(req, res, targetPort, rewritePath = (path) => path, headerOverrides = {}) {
  const parsed = new URL(req.url, "http://localhost");
  const targetPath = rewritePath(parsed.pathname) + parsed.search;
  const headers = {
    ...req.headers,
    ...headerOverrides,
    host: `${GATEWAY_HOST}:${targetPort}`,
    "x-forwarded-host": req.headers.host || "",
    "x-forwarded-proto": "https",
  };

  const proxy = http.request(
    {
      hostname: GATEWAY_HOST,
      port: targetPort,
      method: req.method,
      path: targetPath,
      headers,
    },
    (upstream) => {
      if (res.headersSent) return;
      res.writeHead(upstream.statusCode || 502, upstream.headers);
      upstream.pipe(res);
    },
  );

  proxy.on("error", (error) => {
    err(`Proxy error to port ${targetPort}`, error);
    sendResponse(res, 502, "application/json", JSON.stringify({ error: "proxy_error", message: error.message }));
  });

  req.pipe(proxy);
}

const server = http.createServer(async (req, res) => {
  try {
    const parsed = new URL(req.url, "http://localhost");
    const path = parsed.pathname;

    // Health checks - no auth required
    if (path === "/health" || path === "/status") {
      const data = await statusPayload();
      return sendResponse(res, 200, "application/json", JSON.stringify(data));
    }

    if (path === LOGIN_PATH) {
        return await handleLogin(req, res, parsed);
    }

    if (path === "/api/is-private") {
        if (!_privacyDetectionDone) await privacyDetectionReady;
        return sendResponse(res, 200, "application/json", JSON.stringify({ isPrivate: SPACE_IS_PRIVATE }));
    }

    // Root redirect
    if (path === "/") {
        return redirect(res, `${APP_BASE}/`);
    }

    // Auth guard for all other routes
    if (!isAuthorized(req)) {
        if (wantsHtml(req)) {
            return redirect(res, loginUrl(path + parsed.search));
        }
        return sendResponse(res, 401, "application/json", JSON.stringify({ error: "unauthorized" }));
    }

    // Routing
    if (path.startsWith(APP_BASE)) {
        return proxyRequest(req, res, DASHBOARD_PORT, (p) => p.replace(/^\/app/, "") || "/");
    }

    if (path.startsWith(TERMINAL_BASE)) {
        const up = await canConnect(JUPYTER_PORT);
        if (!up) return sendResponse(res, 503, "text/plain", "Terminal service starting...");

        const jToken = process.env.JUPYTER_TOKEN || API_SERVER_KEY;
        if (jToken && wantsHtml(req) && !parsed.searchParams.has("token")) {
            return redirect(res, `${path}${parsed.search}${parsed.search ? "&" : "?"}token=${jToken}`);
        }
        return proxyRequest(req, res, JUPYTER_PORT, (p) => p, { authorization: `token ${jToken}` });
    }

    if (path.startsWith("/v1")) {
        return proxyRequest(req, res, GATEWAY_PORT);
    }

    // Fallback to dashboard for static assets
    return proxyRequest(req, res, DASHBOARD_PORT);

  } catch (caught) {
    err("Global server error", caught);
    sendResponse(res, 500, "text/plain", "Internal Server Error");
  }
});

server.on("upgrade", (req, socket, head) => {
  const { pathname } = new URL(req.url, "http://localhost");
  const isJupyter = pathname.startsWith(TERMINAL_BASE);
  const targetPort = isJupyter ? JUPYTER_PORT : DASHBOARD_PORT;

  const ps = net.createConnection(targetPort, GATEWAY_HOST, () => {
    ps.write(`${req.method} ${req.url} HTTP/${req.httpVersion}\r\n`);
    ps.write(`Host: ${GATEWAY_HOST}:${targetPort}\r\n`);
    ps.write("X-Forwarded-Proto: https\r\n");

    // Inject Origin for dashboard WS
    if (!isJupyter) {
        ps.write(`Origin: http://${GATEWAY_HOST}:${targetPort}\r\n`);
    }

    for (let i = 0; i < req.rawHeaders.length; i += 2) {
      const lower = req.rawHeaders[i].toLowerCase();
      if (["host", "origin", "x-forwarded-proto"].includes(lower)) continue;
      ps.write(`${req.rawHeaders[i]}: ${req.rawHeaders[i + 1]}\r\n`);
    }
    ps.write("\r\n");
    if (head && head.length) ps.write(head);
    ps.pipe(socket).pipe(ps);
  });
  ps.on("error", () => socket.destroy());
  ps.on("close", () => socket.destroy());
  socket.on("error", () => ps.destroy());
  socket.on("close", () => ps.destroy());
});

server.listen(PORT, "0.0.0.0", () => {
  log(`Money Maker 🤑 proxy server listening on 0.0.0.0:${PORT}`);
});
