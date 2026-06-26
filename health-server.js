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
            return content.split("\n").slice(-20).join("\n")
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");
        }
    } catch (e) {}
    return "Waiting for dashboard to start...";
}

const server = http.createServer((req, res) => {
    const url = req.url.split("?")[0];

    if (url === "/health" || url === "/status") {
        res.writeHead(200, { "Content-Type": "application/json" });
        return res.end(JSON.stringify({ ok: true, uptime: process.uptime() }));
    }

    // Proxy logic
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
        headers: headers
    }, (targetRes) => {
        res.writeHead(targetRes.statusCode, targetRes.headers);
        targetRes.pipe(res);
    });

    proxy.on("error", () => {
        // Backend is down. Try serving local static file or show warming up page.
        const localPath = path.join(UI_DIR, url === "/" ? "index.html" : url);
        if (fs.existsSync(localPath) && !fs.lstatSync(localPath).isDirectory()) {
            const ext = path.extname(localPath);
            const mime = { ".html": "text/html", ".js": "application/javascript", ".css": "text/css", ".png": "image/png", ".jpg": "image/jpeg" }[ext] || "text/plain";
            res.writeHead(200, { "Content-Type": mime });
            return fs.createReadStream(localPath).pipe(res);
        }

        if (!res.headersSent) {
            res.writeHead(503, { "Content-Type": "text/html; charset=utf-8" });
            const logs = getDashboardLogs();
            res.end(`
                <!DOCTYPE html><html><head><meta charset="utf-8"><title>Money Maker 🤑 - Engine Start</title><style>body { background: #0b0e14; color: #e1e1e1; font-family: sans-serif; display: flex; height: 100vh; margin: 0; align-items: center; justify-content: center; text-align: center; }h1 { color: #10a37f; }pre { background: #1a1d23; color: #888; padding: 15px; border-radius: 6px; text-align: left; font-size: 11px; white-space: pre-wrap; border: 1px solid #333; max-width: 800px; width: 90vw; overflow-x: auto; }</style><script>setTimeout(() => {
                    fetch("/status").then(r => r.json()).then(data => { if(data.ok) location.reload(); });
                }, 5000);</script></head><body><div><h1>Money Maker 🤑</h1><p>Engine is warming up. Please wait...</p><pre><b>SYSTEM LOGS:</b>\n${logs}</pre></div></body></html>
            `);
        }
    });

    req.pipe(proxy);
});

// Fix WebSocket upgrade
server.on("upgrade", (req, socket, head) => {
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
    ps.on("error", () => socket.destroy());
    socket.on("error", () => ps.destroy());
});

server.listen(PORT, "0.0.0.0", () => log(`Money Maker Proxy (v2.1) listening on port ${PORT}`));
