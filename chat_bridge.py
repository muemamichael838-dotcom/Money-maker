from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import asyncio
import json
import os

app = FastAPI()

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
        if not message:
            raise HTTPException(status_code=400, detail="Missing message")

        # We'll use the one-shot mode of the agent to get a response
        # In a real 2029 scenario, we would use a persistent process, but for this bridge:
        proc = await asyncio.create_subprocess_exec(
            "python3", "-m", "hermes_cli.main", "-z", message,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            err_msg = stderr.decode().strip()
            print(f"Agent Error: {err_msg}")
            return {"response": f"System Error: {err_msg or 'Unknown agent failure'}", "status": "error"}

        return {"response": stdout.decode().strip(), "status": "success"}
    except Exception as e:
        return {"response": f"Gateway Error: {str(e)}", "status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8642)
