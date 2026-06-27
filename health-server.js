"use strict";

const http = require("http");
const net = require("net");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 10000;
const GATEWAY_HOST = "127.0.0.1";
const DASHBOARD_PORT = 9119;
const HOME = process.env.MONEY_MAKER_HOME || "/opt/data";
const UI_DIR = path.join(__dirname, "money-maker-ui");

const log = (m) => console.log(`[${new Date().toISOString()}] [health-server] ${m}`);

function getDashboardLogs() {
    try {
        const logFile = path.join(HOME, "logs", "dashboard.log");
        if (fs.existsSync(logFile)) {
            const content = fs.readFileSync(logFile, "utf8");
            return content.split("\n").slice(-30).join("\n")
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");
        }
    } catch (e) {}
    return "Initializing system logs...";
}

const server = http.createServer((req, res) => {
    const url = req.url.split("?")[0];

    // Standard health checks for Render/Cloudflare
    if (url === "/health" || url === "/status") {
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        return res.end(JSON.stringify({ ok: true, uptime: process.uptime(), engine: "Money Maker 🤑" }));
    }

    // Proxy request to the main dashboard
    const headers = { ...req.headers };
    headers["host"] = `127.0.0.1:${DASHBOARD_PORT}`;
    headers["x-forwarded-host"] = req.headers.host || "";
    headers["x-forwarded-proto"] = "https";
    headers["x-forwarded-for"] = req.socket.remoteAddress;

    const proxy = http.request({
        hostname: GATEWAY_HOST,
        port: DASHBOARD_PORT,
        path: req.url,
        method: req.method,
        headers: headers,
        timeout: 10000
    }, (targetRes) => {
        // Handle 401/403 at the root if needed, but usually we let the UI handle it
        res.writeHead(targetRes.statusCode, targetRes.headers);
        targetRes.pipe(res);
    });

    proxy.on("error", (err) => {
        // Backend is likely still starting up.
        // 1. Try to serve static assets directly if possible (Fail-fast UI)
        const localPath = path.join(UI_DIR, url === "/" ? "index.html" : url);
        if (fs.existsSync(localPath) && !fs.lstatSync(localPath).isDirectory()) {
            const ext = path.extname(localPath);
            const mime = {
                ".html": "text/html", ".js": "application/javascript", ".css": "text/css",
                ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".ico": "image/x-icon"
            }[ext] || "text/plain";
            res.writeHead(200, { "Content-Type": mime });
            return fs.createReadStream(localPath).pipe(res);
        }

        // 2. If it's a critical path or root, show the branded loading screen
        if (!res.headersSent) {
            res.writeHead(503, { "Content-Type": "text/html; charset=utf-8" });
            const logs = getDashboardLogs();
            res.end(`
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>Money Maker 🤑 | Core Initialization</title>
                    <style>
                        body { background: #09090b; color: #ececec; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; height: 100vh; margin: 0; align-items: center; justify-content: center; }
                        .container { text-align: center; max-width: 600px; width: 90%; }
                        h1 { color: #10a37f; font-weight: 900; letter-spacing: -0.05em; margin-bottom: 10px; }
                        p { color: #71717a; font-size: 14px; margin-bottom: 30px; }
                        .loader { width: 40px; height: 40px; border: 3px solid #10a37f; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
                        pre { background: #18181b; color: #52525b; padding: 20px; border-radius: 12px; text-align: left; font-size: 11px; white-space: pre-wrap; border: 1px solid #27272a; max-height: 300px; overflow-y: auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
                        @keyframes spin { to { transform: rotate(360deg); } }
                    </style>
                    <script>
                        setInterval(() => {
                            fetch("/status").then(r => r.json()).then(data => {
                                if(data.ok) {
                                    // Brief delay to ensure dashboard socket is ready
                                    setTimeout(() => location.reload(), 1000);
                                }
                            }).catch(() => {});
                        }, 3000);
                    </script>
                </head>
                <body>
                    <div class="container">
                        <div class="loader"></div>
                        <h1>Money Maker 🤑</h1>
                        <p>Synchronizing neural layers and establishing secure link...</p>
                        <pre><b>INTERNAL TELEMETRY:</b>\n${logs}</pre>
                    </div>
                </body>
                </html>
            `);
        }
    });

    req.pipe(proxy);
});

// Robust WebSocket proxy for PTY/Xterm
server.on("upgrade", (req, socket, head) => {
    log(`Upgrading connection: ${req.url}`);
    const ps = net.createConnection(DASHBOARD_PORT, GATEWAY_HOST, () => {
        ps.write(`${req.method} ${req.url} HTTP/${req.httpVersion}\r\n`);
        ps.write(`Host: 127.0.0.1:${DASHBOARD_PORT}\r\n`);
        ps.write(`Origin: http://127.0.0.1:${DASHBOARD_PORT}\r\n`);
        for (let i = 0; i < req.rawHeaders.length; i += 2) {
            const lowKey = req.rawHeaders[i].toLowerCase();
            if (lowKey === "host" || lowKey === "origin") continue;
            ps.write(`${req.rawHeaders[i]}: ${req.rawHeaders[i + 1]}\r\n`);
        }
        ps.write("\r\n");
        if (head && head.length) ps.write(head);
        ps.pipe(socket).pipe(ps);
    });

    ps.on("error", (err) => {
        log(`Proxy socket error: ${err.message}`);
        socket.destroy();
    });
    socket.on("error", (err) => {
        log(`Client socket error: ${err.message}`);
        ps.destroy();
    });
});

server.listen(PORT, "0.0.0.0", () => log(`Money Maker Edge (v2.2) active on port ${PORT}`));
