"use strict";

const http = require("http");
const net = require("net");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 10000;
const DASHBOARD_PORT = 9119;
const HOME = process.env.MONEY_MAKER_HOME || "/opt/data";

const log = (m) => console.log(`[${new Date().toISOString()}] [health-server] ${m}`);

function getDashboardLogs() {
    try {
        const logFile = path.join(HOME, "logs", "dashboard.log");
        if (fs.existsSync(logFile)) {
            // Read last 30 lines and sanitize for HTML
            const content = fs.readFileSync(logFile, "utf8");
            return content.split("\n").slice(-30).join("\n")
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");
        }
    } catch (e) {}
    return "No logs found. The engine might be failing to start or permissions are restricted.";
}

const server = http.createServer((req, res) => {
    const url = req.url;

    if (url === "/health" || url === "/status") {
        res.writeHead(200, { "Content-Type": "application/json" });
        return res.end(JSON.stringify({ ok: true, uptime: process.uptime() }));
    }

    // Proxy logic
    const proxy = http.request({
        hostname: "127.0.0.1",
        port: DASHBOARD_PORT,
        path: url,
        method: req.method,
        headers: req.headers
    }, (targetRes) => {
        if (!res.headersSent) {
            res.writeHead(targetRes.statusCode, targetRes.headers);
            targetRes.pipe(res);
        }
    });

    proxy.on("error", (e) => {
        if (!res.headersSent) {
            res.writeHead(503, { "Content-Type": "text/html; charset=utf-8" });
            const logs = getDashboardLogs();
            res.end(`
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>Money Maker 🤑 - Starting Up</title>
                    <style>
                        body { background: #0b0e14; color: #e1e1e1; font-family: -apple-system, sans-serif; display: flex; height: 100vh; margin: 0; align-items: center; justify-content: center; text-align: center; }
                        .box { max-width: 90%; width: 600px; padding: 20px; background: #1a1d23; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
                        h1 { color: #10a37f; margin-top: 0; }
                        .loader { border: 4px solid #2d3139; border-top: 4px solid #10a37f; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
                        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                        pre { background: #0b0e14; color: #888; padding: 15px; border-radius: 6px; text-align: left; font-size: 11px; overflow-x: auto; white-space: pre-wrap; border: 1px solid #333; max-height: 300px; overflow-y: auto; }
                        .status { font-size: 14px; margin-bottom: 20px; opacity: 0.8; }
                        .btn { background: #10a37f; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; text-decoration: none; font-weight: bold; font-size: 14px; }
                    </style>
                    <script>setTimeout(() => location.reload(), 8000);</script>
                </head>
                <body>
                    <div class="box">
                        <h1>Money Maker 🤑</h1>
                        <div class="loader"></div>
                        <div class="status">Dashboard is warming up. This usually takes 30-60 seconds.</div>
                        <pre><b>ENGINE DIAGNOSTICS:</b>\n\n${logs}</pre>
                        <p><a href="javascript:location.reload()" class="btn">Manual Refresh</a></p>
                    </div>
                </body>
                </html>
            `);
        }
    });

    req.pipe(proxy);
});

server.listen(PORT, "0.0.0.0", () => log(`Money Maker Proxy listening on port ${PORT}`));
