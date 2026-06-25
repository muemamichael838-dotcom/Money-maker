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
const TELEGRAM_WEBHOOK_PORT = 8000; // api_proxy.py also used for LLM fallback but can handle TG if configured

const API_SERVER_KEY = process.env.GATEWAY_TOKEN || "";
const APP_BASE = "/app";
const TERMINAL_BASE = "/terminal";
const LOGIN_PATH = "/login";

const SPACE_ID = process.env.SPACE_ID || "";
const SPACE_AUTHOR_NAME = process.env.SPACE_AUTHOR_NAME || "";
const SPACE_REPO_NAME = process.env.SPACE_REPO_NAME || "";
const HF_SPACE_URL = SPACE_ID ? `https://huggingface.co/spaces/${SPACE_ID}` : "";

let SPACE_IS_PRIVATE = !!SPACE_ID;
let _privacyDetectionDone = false;

const privacyDetectionReady = (async () => {
  if (!SPACE_ID) {
    _privacyDetectionDone = true;
    return;
  }
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
    }
  } catch (e) {
    console.error("[health-server] Privacy detection failed:", e.message);
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

function requireAuth(req, res) {
  if (isAuthorized(req)) return true;
  if (wantsHtml(req)) {
    const parsed = new URL(req.url, "http://localhost");
    redirect(res, loginUrl(`${parsed.pathname}${parsed.search}`));
    return false;
  }
  res.writeHead(401, { "content-type": "application/json" });
  res.end(JSON.stringify({ error: "unauthorized" }));
  return false;
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
        res.writeHead(302, {
          location: params.get("next") || "/",
          "set-cookie": `token=${password}; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000`,
        });
        res.end();
      } else {
        res.writeHead(200, { "content-type": "text/html" });
        res.end(renderLoginPage("Invalid password.", params.get("next")));
      }
    });
    return;
  }
  res.writeHead(200, { "content-type": "text/html" });
  res.end(renderLoginPage("", parsed.searchParams.get("next")));
}

function renderLoginPage(error = "", next = "") {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Money Maker 🤑</title>
  <style>
    body { background: #0b0e14; color: #e1e1e1; font-family: -apple-system, sans-serif; display: flex; height: 100vh; margin: 0; align-items: center; justify-content: center; }
    .card { background: #1a1d23; padding: 2.5rem; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 100%; max-width: 400px; text-align: center; }
    h1 { margin-top: 0; color: #10a37f; font-size: 1.5rem; }
    input { width: 100%; padding: 0.8rem; margin: 1.5rem 0; background: #2d3139; border: 1px solid #3e4451; border-radius: 6px; color: white; box-sizing: border-box; font-size: 1rem; }
    button { background: #10a37f; color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; font-size: 1rem; }
    button:hover { background: #1a7f64; }
    .error { color: #ff4b4b; margin-top: 1rem; font-size: 0.9rem; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🪽 Money Maker 🤑</h1>
    <p>Please enter your Gateway Token.</p>
    <form method="POST">
      <input type="hidden" name="next" value="${next || ""}">
      <input type="password" name="password" placeholder="••••••••" required autofocus>
      <button type="submit">Unlock Dashboard</button>
      ${error ? `<div class="error">${error}</div>` : ""}
    </form>
  </div>
</body>
</html>`;
}

function renderPrivateRedirect(url) {
  return `<!DOCTYPE html><html><head><title>Money Maker 🤑 — Private Space</title><meta http-equiv="refresh" content="0; url=${url}"></head><body>Redirecting to <a href="${url}">${url}</a>...</body></html>`;
}

function canConnect(port) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    socket.setTimeout(500);
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
    auth: !!API_SERVER_KEY,
  };
}

function proxyRequest(
  req,
  res,
  targetPort,
  rewritePath = (path) => path,
  headerOverrides = {},
) {
  const parsed = new URL(req.url, "http://localhost");
  const targetPath = rewritePath(parsed.pathname) + parsed.search;
  const headers = {
    ...req.headers,
    ...headerOverrides,
    host: `${GATEWAY_HOST}:${targetPort}`,
    "x-forwarded-host": req.headers.host || "",
    "x-forwarded-proto": req.headers["x-forwarded-proto"] || "https",
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
      res.writeHead(upstream.statusCode || 502, upstream.headers);
      upstream.pipe(res);
    },
  );

  proxy.on("error", (error) => {
    if (!res.headersSent) {
      res.writeHead(502, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: "proxy_error", message: error.message }));
    }
  });

  req.pipe(proxy);
}

function redirect(res, location, statusCode = 302) {
  res.writeHead(statusCode, { location });
  res.end();
}

const server = http.createServer(async (req, res) => {
  try {
    const parsed = new URL(req.url, "http://localhost");
    const path = parsed.pathname;

    if (path === "/api/is-private") {
      if (!_privacyDetectionDone) await privacyDetectionReady;
      res.writeHead(200, { "content-type": "application/json", "cache-control": "no-store" });
      return res.end(JSON.stringify({ isPrivate: SPACE_IS_PRIVATE }));
    }

    if (path === LOGIN_PATH) {
      await handleLogin(req, res, parsed);
      return;
    }

    const isHtmlReq = (req.headers.accept || "").includes("text/html");

    if (isHtmlReq && !_privacyDetectionDone) {
      await Promise.race([
        privacyDetectionReady,
        new Promise((r) => setTimeout(r, 1500)),
      ]);
    }

    const referer = req.headers.referer || req.headers.referrer || "";
    const isSameOriginNav = !!(referer && typeof req.headers.host === "string" &&
      referer.startsWith(`https://${req.headers.host}`));
    const isFromHFApp = !!(referer && (
      referer.startsWith("https://huggingface.co") ||
      referer.startsWith("https://hf.co")
    ));

    const isDirectHfSpaceReq = SPACE_IS_PRIVATE &&
      HF_SPACE_URL &&
      isHtmlReq &&
      !isSameOriginNav &&
      !isFromHFApp &&
      typeof req.headers.host === "string" &&
      req.headers.host.endsWith(".hf.space");

    if (path === "/hf-redirect" || path === "/hf-redirect/") {
      if (HF_SPACE_URL) {
        res.writeHead(302, { location: HF_SPACE_URL, "cache-control": "no-store" });
        return res.end();
      }
      res.writeHead(404, { "content-type": "text/plain" });
      return res.end("SPACE_ID not configured.");
    }

    if (path === "/health" || path === `${APP_BASE}/health`) {
      const data = await statusPayload();
      res.writeHead(200, { "content-type": "application/json" });
      res.end(
        JSON.stringify({
          ok: data.ok,
          gateway: data.gateway,
          uptime: data.uptime,
        }),
      );
      return;
    }

    if (path === "/status" || path === `${APP_BASE}/status`) {
      const data = await statusPayload();
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify(data, null, 2));
      return;
    }

    if (path === "/env-builder" || path === "/env-builder/") {
      if (!requireAuth(req, res)) return;
      try {
        const html = fs.readFileSync(require("path").join(__dirname, "env-builder.html"), "utf8");
        res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
        res.end(html);
      } catch (e) {
        res.writeHead(404, { "content-type": "text/plain" });
        res.end("env-builder.html not found");
      }
      return;
    }

    if (path === "/env-builder.js") {
      if (!requireAuth(req, res)) return;
      try {
        const js = fs.readFileSync(require("path").join(__dirname, "env-builder.js"), "utf8");
        res.writeHead(200, { "content-type": "application/javascript; charset=utf-8" });
        res.end(js);
      } catch (e) {
        res.writeHead(404, { "content-type": "text/plain" });
        res.end("env-builder.js not found");
      }
      return;
    }

    if (path === "/") {
      if (isDirectHfSpaceReq) {
        res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
        return res.end(renderPrivateRedirect(HF_SPACE_URL));
      }
      // Fixed: Removed redundant writeHead(200) before redirect
      redirect(res, `${APP_BASE}/`);
      return;
    }

    if (path === "/dashboard" || path === "/dashboard/") {
      redirect(res, `${APP_BASE}/${parsed.search}`);
      return;
    }

    if (path === "/telegram" || path.startsWith("/telegram/")) {
      proxyRequest(req, res, TELEGRAM_WEBHOOK_PORT);
      return;
    }

    if (path === APP_BASE || path.startsWith(`${APP_BASE}/`)) {
      if (!requireAuth(req, res)) return;
      proxyRequest(
        req,
        res,
        DASHBOARD_PORT,
        (p) => p.replace(/^\/app/, "") || "/",
      );
      return;
    }

    if (
      path === "/favicon.ico" ||
      path.startsWith("/assets/") ||
      path.startsWith("/api/") ||
      path.startsWith("/dashboard-plugins/") ||
      path.startsWith("/ds-assets/")
    ) {
      if (!requireAuth(req, res)) return;
      proxyRequest(req, res, DASHBOARD_PORT);
      return;
    }

    if (
      [
        "/analytics",
        "/chat",
        "/config",
        "/cron",
        "/docs",
        "/env",
        "/logs",
        "/models",
        "/plugins",
        "/profiles",
        "/sessions",
        "/skills",
      ].some((route) => path === route || path.startsWith(`${route}/`))
    ) {
      redirect(res, `${APP_BASE}${path}${parsed.search}`);
      return;
    }

    if (path === "/v1" || path.startsWith("/v1/")) {
      if (!isAuthorized(req)) {
        if (wantsHtml(req)) {
          redirect(res, loginUrl(`${path}${parsed.search}`));
          return;
        }
        res.writeHead(401, {
          "content-type": "application/json",
          "cache-control": "no-store",
        });
        res.end(
          JSON.stringify({
            error: "unauthorized",
            message: "Use Authorization: Bearer <GATEWAY_TOKEN>.",
          }),
        );
        return;
      }
      const upstreamHeaders =
        getBearerToken(req) || !API_SERVER_KEY
          ? {}
          : { authorization: `Bearer ${API_SERVER_KEY}` };
      proxyRequest(req, res, GATEWAY_PORT, (p) => p, upstreamHeaders);
      return;
    }

    if (path === TERMINAL_BASE || path.startsWith(`${TERMINAL_BASE}/`)) {
      if (!requireAuth(req, res)) return;
      canConnect(JUPYTER_PORT).then((up) => {
        if (!up) {
          res.writeHead(503, { "content-type": "text/plain; charset=utf-8" });
          res.end("JupyterLab is not running. GATEWAY_TOKEN must be set, and DEV_MODE must not be false.");
          return;
        }
        const rawJToken = (process.env.JUPYTER_TOKEN || "").trim();
        const jToken = rawJToken || API_SERVER_KEY;
        if (jToken && isHtmlReq) {
          const parsed2 = new URL(req.url, "http://localhost");
          if (!parsed2.searchParams.has("token")) {
            const sep = parsed2.search ? "&" : "?";
            redirect(res, `${parsed2.pathname}${parsed2.search}${sep}token=${encodeURIComponent(jToken)}`);
            return;
          }
        }
        const overrides = jToken ? { authorization: `token ${jToken}` } : {};
        proxyRequest(req, res, JUPYTER_PORT, (p) => p, overrides);
      });
      return;
    }

    res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
    res.end("Not found");
  } catch (err) {
    console.error("[health-server] Request error:", err);
    if (!res.headersSent) {
      res.writeHead(500, { "content-type": "text/plain" });
      res.end("Internal Server Error");
    }
  }
});

server.on("upgrade", (req, socket, head) => {
  const { pathname } = new URL(req.url, "http://localhost");
  const isJupyter = pathname === TERMINAL_BASE || pathname.startsWith(`${TERMINAL_BASE}/`);
  const isDashboardWs =
      pathname === "/api/pty" ||
      pathname === "/api/events" ||
      pathname === "/api/ws";
  const targetPort = isJupyter
      ? JUPYTER_PORT
      : isDashboardWs
          ? DASHBOARD_PORT
          : GATEWAY_PORT;
  const ps = net.createConnection(targetPort, GATEWAY_HOST, () => {
    ps.write(`${req.method} ${req.url} HTTP/${req.httpVersion}\r\n`);
    ps.write(`Host: ${GATEWAY_HOST}:${targetPort}\r\n`);
    ps.write(`X-Forwarded-Host: ${req.headers.host || ""}\r\n`);
    ps.write("X-Forwarded-Proto: https\r\n");
    const skip = ["host", "x-forwarded-host", "x-forwarded-proto"];
    if (isDashboardWs) {
      ps.write(`Origin: http://${GATEWAY_HOST}:${targetPort}\r\n`);
      skip.push("origin");
    }
    for (let i = 0; i < req.rawHeaders.length; i += 2) {
      const lower = req.rawHeaders[i].toLowerCase();
      if (skip.includes(lower)) continue;
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

server.timeout = 0;
server.keepAliveTimeout = 65000;
console.log(`[health-server] Attempting to bind to 0.0.0.0:${PORT}...`);
server.listen(PORT, "0.0.0.0", () => {
  console.log(`Money Maker 🤑 dashboard listening on 0.0.0.0:${PORT}`);
});
