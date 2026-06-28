import os
import json
import random
import requests
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from persistence_manager import PersistenceManager

app = FastAPI()
pm = PersistenceManager()

# Global state for key rotation to ensure we don't just keep picking the same failed key
ROTATION_STATE = {}

def get_pools():
    """
    Retrieves API key pools from environment variables and persistence.
    Supports comma-separated strings.
    """
    pools = {
        "groq": (os.environ.get("GROQ_API_KEYS") or "").split(","),
        "huggingface": (os.environ.get("HUGGINGFACE_API_KEYS") or "").split(","),
        "google": (os.environ.get("GOOGLE_API_KEYS") or "").split(","),
    }

    # Layer in values from Persistence (Settings) saved via UI
    saved_settings = pm.get_memory("api_settings") or {}
    if "groq" in saved_settings: pools["groq"].extend(saved_settings["groq"].split(","))
    if "hf" in saved_settings: pools["huggingface"].extend(saved_settings["hf"].split(","))
    if "google" in saved_settings: pools["google"].extend(saved_settings["google"].split(","))

    # Clean, trim, and filter empty strings
    for p in pools:
        pools[p] = [k.strip() for k in pools[p] if k.strip()]
    return pools

PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "header_type": "Bearer"
    },
    "huggingface": {
        "url": "https://api-inference.huggingface.co/models/{model}/v1/chat/completions",
        "header_type": "Bearer"
    },
    "google": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "header_type": "Bearer"
    }
}

def select_key(provider, pool):
    """Selects a key from the pool, implementing basic round-robin via rotation state."""
    if not pool: return None

    if provider not in ROTATION_STATE:
        ROTATION_STATE[provider] = 0
    else:
        ROTATION_STATE[provider] = (ROTATION_STATE[provider] + 1) % len(pool)

    return pool[ROTATION_STATE[provider]]

@app.get("/health")
async def health():
    pools = get_pools()
    active = {p: len(v) for p, v in pools.items() if v}
    return {
        "status": "online",
        "engine": "Money Maker Multi-Key Proxy",
        "active_pools": active
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    model = body.get("model", "").lower()

    # Determine provider based on model string
    provider = "groq"
    if any(x in model for x in ["hf-", "huggingface", "llama-3-70b-instruct"]):
        provider = "huggingface"
    elif any(x in model for x in ["gemini", "google"]):
        provider = "google"
    elif "groq" in model:
        provider = "groq"

    config = PROVIDERS.get(provider)
    if not config:
        # Fallback to groq as default if ambiguous
        provider = "groq"
        config = PROVIDERS["groq"]

    target_url = config["url"].format(model=body.get("model")) if "{model}" in config["url"] else config["url"]

    pools = get_pools()
    pool = pools.get(provider, [])

    if not pool:
        pm.log("ERROR", f"No API keys available for provider: {provider}")
        raise HTTPException(status_code=400, detail=f"No API keys configured for {provider}")

    last_error = ""
    # Try up to the total number of keys in the pool + 1 (for good measure)
    max_tries = min(len(pool) * 2, 5)

    for attempt in range(max_tries):
        api_key = select_key(provider, pool)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            start_time = time.time()
            response = requests.post(target_url, headers=headers, json=body, timeout=60)
            duration = time.time() - start_time

            if response.status_code == 200:
                pm.log("DEBUG", f"Request successful via {provider} ({duration:.2f}s)")
                return response.json()

            # If 401/403 or 429, we definitely want to rotate
            pm.log("WARN", f"Key failure on {provider} (Status {response.status_code}). Rotating...")
            last_error = f"Status {response.status_code}: {response.text}"

        except Exception as e:
            pm.log("ERROR", f"Request exception on {provider}: {str(e)}")
            last_error = str(e)
            continue

    pm.log("CRITICAL", f"All key rotation attempts failed for {provider}. Last error: {last_error}")
    raise HTTPException(status_code=500, detail=f"Neural failure: All available keys for {provider} are exhausted or invalid. Details: {last_error}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
