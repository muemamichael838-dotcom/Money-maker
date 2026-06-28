"use strict";

const http = require("http");
const net = require("net");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 7860; // HF Spaces Port
const GATEWAY_HOST = "127.0.0.1";
const DASHBOARD_PORT = 9119;
const CHAT_BRIDGE_PORT = 8642;
const UI_DIR = path.join(__dirname, "money-maker-ui");
const LOG_FILE = path.join(process.env.MONEY_MAKER_HOME || "/opt/data", "agent.log");

const log = (m) => console.log(`[${new Date().toISOString()}] [Edge-Router] ${m}`);

const server = http.createServer((req, res) => {
    const url = req.url.split("?")[0];

    // Health Checks
    if (url === "/health" || url === "/status") {
        res.writeHead(200, { "Content-Type": "application/json" });
        return res.end(JSON.stringify({
            ok: true,
            status: "Running",
            engine: "Money Maker 🤑",
            node_version: process.version
        }));
    }

    // Chat API Routing
    if (url.startsWith("/api/chat") || url.startsWith("/api/skills") || url.startsWith("/api/settings")) {
        return proxyRequest(req, res, CHAT_BRIDGE_PORT);
    }

    // Static UI Servicing
    let localPath = path.join(UI_DIR, url === "/" ? "index.html" : url);
    if (fs.existsSync(localPath) && fs.lstatSync(localPath).isFile()) {
        const ext = path.extname(localPath);
        const mime = {
            ".html": "text/html", ".js": "application/javascript", ".css": "text/css",
            ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml"
        }[ext] || "text/plain";
        res.writeHead(200, { "Content-Type": mime });
        return fs.createReadStream(localPath).pipe(res);
    }

    // Default: Proxy to Dashboard (Root Shell / Internal Tools)
    proxyRequest(req, res, DASHBOARD_PORT);
});

function proxyRequest(req, res, targetPort) {
    const proxy = http.request({
        hostname: GATEWAY_HOST,
        port: targetPort,
        path: req.url,
        method: req.method,
        headers: req.headers,
        timeout: 120000 // High timeout for long-running AI tasks
    }, (targetRes) => {
        res.writeHead(targetRes.statusCode, targetRes.headers);
        targetRes.pipe(res);
    });

    proxy.on("error", (err) => {
        if (!res.headersSent) {
            res.writeHead(503, { "Content-Type": "text/html" });
            const logs = fs.existsSync(LOG_FILE) ? fs.readFileSync(LOG_FILE, "utf8").split("\n").slice(-10).join("\n") : "System Booting...";
            res.end(`
                <body style="background:#09090b;color:#10a37f;font-family:monospace;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;">
                    <h1>Money Maker 🤑 Waking Up...</h1>
                    <pre style="background:#18181b;padding:20px;border-radius:10px;width:80%;overflow:auto;color:#52525b;">${logs}</pre>
                    <script>setTimeout(() => location.reload(), 3000);</script>
                </body>
            `);
        }
    });

    req.pipe(proxy);
}

// Support WebSockets for the Root Shell
server.on("upgrade", (req, socket, head) => {
    const targetPort = req.url.includes("pty") ? DASHBOARD_PORT : DASHBOARD_PORT;
    const ps = net.createConnection(targetPort, GATEWAY_HOST, () => {
        ps.write(`${req.method} ${req.url} HTTP/${req.httpVersion}\r\n`);
        for (let i = 0; i < req.rawHeaders.length; i += 2) {
            ps.write(`${req.rawHeaders[i]}: ${req.rawHeaders[i + 1]}\r\n`);
        }
        ps.write("\r\n");
        if (head && head.length) ps.write(head);
        ps.pipe(socket).pipe(ps);
    });
    ps.on("error", () => socket.destroy());
    socket.on("error", () => ps.destroy());
});

server.listen(PORT, "0.0.0.0", () => log(`Neural Gateway Matrix deployed on port ${PORT}`));
