from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import asyncio
import json
import os
import uuid
from persistence_manager import PersistenceManager

app = FastAPI()
pm = PersistenceManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        message = body.get("message")
        session_id = body.get("session_id")

        if not message:
            raise HTTPException(status_code=400, detail="Missing message")

        # Build command with session persistence if provided
        cmd = ["python3", "-m", "hermes_cli.main", "-z", message]
        if session_id:
            # We use the session ID to resume or continue
            cmd.extend(["-c", session_id])

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            err_msg = stderr.decode().strip()
            # If it failed because of no model, we return a helpful message
            if "No inference provider configured" in err_msg:
                return {"response": "System Error: No API keys configured. Please go to 'Key Management' to set up your Groq or Google keys.", "status": "error"}
            return {"response": f"System Error: {err_msg or 'Unknown agent failure'}", "status": "error"}

        return {"response": stdout.decode().strip(), "status": "success"}
    except Exception as e:
        return {"response": f"Gateway Error: {str(e)}", "status": "error"}

@app.post("/api/settings")
async def save_settings(request: Request):
    try:
        body = await request.json()
        pm.save_memory("api_settings", body)
        return {"status": "success", "message": "Settings saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skills")
async def get_skills():
    return [
        {"name": "Market Intelligence", "icon": "trending-up", "desc": "Real-time analysis of global financial markets and crypto trends using advanced scraping."},
        {"name": "Neural Web Scraper", "icon": "globe", "desc": "Deep recursive scraping of any website with JavaScript rendering and AI-driven data extraction."},
        {"name": "Sports Analytics", "icon": "trophy", "desc": "Live odds retrieval and predictive modeling for major sports leagues (NBA, NFL, Soccer)."},
        {"name": "Logic Synthesis", "icon": "brain", "desc": "Complex reasoning and problem-solving through multi-step chain-of-thought processing."},
        {"name": "Autonomous Ops", "icon": "zap", "desc": "Self-correcting task execution and background automation via persistent cron managers."},
        {"name": "Knowledge Retrieval", "icon": "library", "desc": "Instant access to Wikipedia and academic databases for verified context and facts."}
    ]

@app.get("/api/sessions")
async def list_sessions():
    try:
        # Get session list from hermes_cli
        proc = await asyncio.create_subprocess_exec(
            "python3", "-m", "hermes_cli.main", "sessions", "list",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        lines = stdout.decode().strip().split('\n')
        # Simple parsing for the UI
        sessions = []
        for line in lines:
            if line and '-' in line:
                sessions.append({"id": line.strip()})
        return sessions
    except Exception:
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8642)
