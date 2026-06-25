"use strict";

const http = require("http");
const https = require("https");
const fs = require("fs");
const net = require("net");
const path = require("path");

const PORT = process.env.PORT || 10000;
const GATEWAY_HOST = "127.0.0.1";
const GATEWAY_PORT = process.env.GATEWAY_API_PORT || 8642;
const DASHBOARD_PORT = process.env.DASHBOARD_PORT || 9119;
const JUPYTER_PORT = process.env.JUPYTER_PORT || 8888;

const API_SERVER_KEY = process.env.GATEWAY_TOKEN || "";
const APP_BASE = "/app";
const TERMINAL_BASE = "/terminal";
const LOGIN_PATH = "/login";
const LOGS_PATH = "/api/logs";

const MONEY_MAKER_HOME = process.env.MONEY_MAKER_HOME || "/opt/data";

const log = (msg) => console.log(`[${new Date().toISOString()}] [health-server] ${msg}`);
const err = (msg, error) => console.error(`[${new Date().toISOString()}] [health-server] ERROR: ${msg}`, error || "");

function isAuthorized(req) {
  if (!API_SERVER_KEY) return true;
  const cookieHeader = req.headers.cookie || "";
  const cookies = Object.fromEntries(cookieHeader.split(";").map((c) => c.trim().split("=")));
  if (cookies.token === API_SERVER_KEY) return true;
  const authHeader = req.headers.authorization || "";
  return authHeader === `Bearer ${API_SERVER_KEY}`;
}

function sendResponse(res, status, type, content) {
    if (res.headersSent) return;
    res.writeHead(status, { "Content-Type": type, "Cache-Control": "no-store" });
    res.end(content);
}

function redirect(res, location, statusCode = 302) {
    if (res.headersSent) return;
    res.writeHead(statusCode, { "Location": location });
    res.end();
}

function wantsHtml(req) { return (req.headers.accept || "").includes("text/html"); }

function canConnect(port) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    socket.setTimeout(300);
    socket.once("connect", () => { socket.destroy(); resolve(true); });
    socket.once("timeout", () => { socket.destroy(); resolve(false); });
    socket.once("error", () => { socket.destroy(); resolve(false); });
    socket.connect(port, GATEWAY_HOST);
  });
}

function proxyRequest(req, res, targetPort, rewritePath = (path) => path, headerOverrides = {}) {
  const parsed = new URL(req.url, "http://localhost");
  const targetPath = rewritePath(parsed.pathname) + parsed.search;
  const headers = { ...req.headers, ...headerOverrides, host: `${GATEWAY_HOST}:${targetPort}`, "x-forwarded-proto": "https" };

  const proxy = http.request({ hostname: GATEWAY_HOST, port: targetPort, method: req.method, path: targetPath, headers }, (upstream) => {
    if (res.headersSent) return;
    res.writeHead(upstream.statusCode || 502, upstream.headers);
    upstream.pipe(res);
  });

  proxy.on("error", (error) => {
    if (error.code === "ECONNREFUSED" && wantsHtml(req)) {
        return sendResponse(res, 503, "text/html", `<!DOCTYPE html><html><head><title>Money Maker 🤑 - Engine Warming</title><style>body { background: #0b0e14; color: white; font-family: sans-serif; display: flex; height: 100vh; margin: 0; align-items: center; justify-content: center; text-align: center; }h1 { color: #10a37f; }.loader { border: 4px solid #f3f3f3; border-top: 4px solid #10a37f; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }.logs { background: #1a1d23; color: #888; font-family: monospace; padding: 10px; border-radius: 4px; font-size: 11px; max-width: 600px; text-align: left; overflow: hidden; margin-top: 20px; }</style><script>setTimeout(() => location.reload(), 5000);</script></head><body><div><h1>Money Maker 🤑</h1><div class="loader"></div><p>Dashboard is initializing. Hang tight...</p><div class="logs">SYSTEM STATUS: Attempting connection to internal port ${targetPort}...</div></div></body></html>`);
    }
    err(`Proxy error to port ${targetPort}`, error);
    sendResponse(res, 502, "application/json", JSON.stringify({ error: "proxy_error", message: error.message }));
  });
  req.pipe(proxy);
}

const server = http.createServer(async (req, res) => {
  try {
    const parsed = new URL(req.url, "http://localhost");
    const pathName = parsed.pathname;

    if (pathName === "/health" || pathName === "/status") {
      const [gateway, dashboard] = await Promise.all([canConnect(GATEWAY_PORT), canConnect(DASHBOARD_PORT)]);
      return sendResponse(res, 200, "application/json", JSON.stringify({ ok: gateway && dashboard, gateway, dashboard, uptime: process.uptime() }));
    }

    if (pathName === LOGIN_PATH) {
      if (req.method === "POST") {
        let body = "";
        req.on("data", chunk => body += chunk);
        req.on("end", () => {
          const params = new URLSearchParams(body);
          if (params.get("password") === API_SERVER_KEY) {
            res.writeHead(302, { location: params.get("next") || "/", "set-cookie": `token=${API_SERVER_KEY}; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000` });
            res.end();
          } else { sendResponse(res, 200, "text/html", renderLoginPage("Invalid.")); }
        });
        return;
      }
      return sendResponse(res, 200, "text/html", renderLoginPage());
    }

    if (pathName === "/") return redirect(res, `${APP_BASE}/`);

    if (!isAuthorized(req)) return wantsHtml(req) ? redirect(res, `${LOGIN_PATH}?next=${encodeURIComponent(pathName)}`) : sendResponse(res, 401, "application/json", '{"error":"unauthorized"}');

    // Logs viewer for emergency debugging
    if (pathName === LOGS_PATH) {
        const logFile = path.join(MONEY_MAKER_HOME, "logs", "dashboard.log");
        if (!fs.existsSync(logFile)) return sendResponse(res, 404, "text/plain", "Log file not found yet.");
        const content = fs.readFileSync(logFile, "utf8").split("\n").slice(-50).join("\n");
        return sendResponse(res, 200, "text/plain", content);
    }

    if (pathName.startsWith(APP_BASE)) return proxyRequest(req, res, DASHBOARD_PORT, p => p.replace(/^\/app/, "") || "/");
    if (pathName.startsWith(TERMINAL_BASE)) {
        const jToken = process.env.JUPYTER_TOKEN || API_SERVER_KEY;
        if (jToken && wantsHtml(req) && !parsed.searchParams.has("token")) return redirect(res, `${pathName}${parsed.search}${parsed.search ? "&" : "?"}token=${jToken}`);
        return proxyRequest(req, res, JUPYTER_PORT, p => p, { authorization: `token ${jToken}` });
    }
    return proxyRequest(req, res, DASHBOARD_PORT);

  } catch (caught) { err("Global server error", caught); sendResponse(res, 500, "text/plain", "Internal Error"); }
});

function renderLoginPage(e="") { return `<!DOCTYPE html><html><head><meta charset="utf-8"><title>Money Maker 🤑</title><style>body { background: #0b0e14; color: white; font-family: sans-serif; display: flex; height: 100vh; margin: 0; align-items: center; justify-content: center; }.card { background: #1a1d23; padding: 2rem; border-radius: 8px; width: 300px; text-align: center; }input { width: 100%; padding: 10px; margin: 15px 0; background: #2d3139; border: 1px solid #3e4451; color: white; border-radius: 4px; box-sizing: border-box; }button { background: #10a37f; color: white; border: none; padding: 10px; width: 100%; border-radius: 4px; cursor: pointer; }</style></head><body><div class="card"><h1>Money Maker</h1><form method="POST"><input type="password" name="password" placeholder="Token" required><button type="submit">Enter</button>${e ? `<div style="color:red">${e}</div>` : ""}</form></div></body></html>`; }

server.on("upgrade", (req, socket, head) => {
  const { pathname } = new URL(req.url, "http://localhost");
  const targetPort = pathname.startsWith(TERMINAL_BASE) ? JUPYTER_PORT : DASHBOARD_PORT;
  const ps = net.createConnection(targetPort, GATEWAY_HOST, () => {
    ps.write(`${req.method} ${req.url} HTTP/${req.httpVersion}\r\n`);
    ps.write(`Host: ${GATEWAY_HOST}:${targetPort}\r\n`);
    if (!pathname.startsWith(TERMINAL_BASE)) ps.write(`Origin: http://${GATEWAY_HOST}:${targetPort}\r\n`);
    for (let i = 0; i < req.rawHeaders.length; i += 2) {
      if (["host", "origin"].includes(req.rawHeaders[i].toLowerCase())) continue;
      ps.write(`${req.rawHeaders[i]}: ${req.rawHeaders[i + 1]}\r\n`);
    }
    ps.write("\r\n");
    if (head && head.length) ps.write(head);
    ps.pipe(socket).pipe(ps);
  });
  ps.on("error", () => socket.destroy());
  socket.on("error", () => ps.destroy());
});

server.listen(PORT, "0.0.0.0", () => { log(`Money Maker 🤑 v1.3 listening on 0.0.0.0:${PORT}`); });
