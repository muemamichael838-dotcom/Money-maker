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

# Global state for key rotation
ROTATION_STATE = {}

def get_pools():
    """
    Retrieves API key pools from environment variables and persistence.
    Supports comma-separated strings and both singular/plural env names.
    """
    # Environment variables (checking both plural and singular)
    groq_env = os.environ.get("GROQ_API_KEYS") or os.environ.get("GROQ_API_KEY") or ""
    hf_env = os.environ.get("HUGGINGFACE_API_KEYS") or os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN") or ""
    google_env = os.environ.get("GOOGLE_API_KEYS") or os.environ.get("GOOGLE_API_KEY") or ""
    openai_env = os.environ.get("OPENAI_API_KEYS") or os.environ.get("OPENAI_API_KEY") or ""

    pools = {
        "groq": groq_env.split(","),
        "huggingface": hf_env.split(","),
        "google": google_env.split(","),
        "openai": openai_env.split(","),
    }

    # Layer in values from Persistence (Settings) saved via UI
    saved_settings = pm.get_memory("api_settings") or {}
    if "groq" in saved_settings and saved_settings["groq"]:
        pools["groq"].extend(saved_settings["groq"].split(","))
    if "hf" in saved_settings and saved_settings["hf"]:
        pools["huggingface"].extend(saved_settings["hf"].split(","))
    if "google" in saved_settings and saved_settings["google"]:
        pools["google"].extend(saved_settings["google"].split(","))
    if "openai" in saved_settings and saved_settings["openai"]:
        pools["openai"].extend(saved_settings["openai"].split(","))

    # Clean, trim, and filter empty strings
    for p in pools:
        pools[p] = [k.strip() for k in pools[p] if k.strip()]

    # Log discovery (masked)
    for provider, keys in pools.items():
        if keys:
            pm.log("INFO", f"Key Discovery: {provider} pool size = {len(keys)}")

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
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
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

    # Safety check
    if ROTATION_STATE[provider] >= len(pool):
        ROTATION_STATE[provider] = 0

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
    model = str(body.get("model", "")).lower()

    # Determine provider based on model string
    provider = "groq"
    if any(x in model for x in ["hf-", "huggingface", "llama-3-70b-instruct"]):
        provider = "huggingface"
    elif any(x in model for x in ["gemini", "google"]):
        provider = "google"
    elif "gpt" in model:
        provider = "openai"
    elif "groq" in model:
        provider = "groq"

    config = PROVIDERS.get(provider) or PROVIDERS["groq"]

    model_name = body.get("model") or "llama-3.3-70b-versatile"
    target_url = config["url"].format(model=model_name) if "{model}" in config["url"] else config["url"]

    pools = get_pools()
    pool = pools.get(provider, [])

    if not pool:
        # If the requested provider has no keys, try fallback to any active pool
        active_providers = [p for p, k in pools.items() if k]
        if active_providers:
            provider = active_providers[0]
            pool = pools[provider]
            config = PROVIDERS[provider]
            pm.log("WARN", f"Requested provider {provider} missing keys. Falling back to {active_providers[0]}")
        else:
            pm.log("ERROR", f"No API keys available for any provider.")
            raise HTTPException(status_code=400, detail="No API keys configured in environment or settings.")

    last_error = ""
    max_tries = min(len(pool) * 2, 5)

    for attempt in range(max_tries):
        api_key = select_key(provider, pool)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            # Strip prefixes if necessary for specific providers
            modified_body = body.copy()
            if provider == "google" and "model" in modified_body and modified_body["model"]:
                if "/" in str(modified_body["model"]):
                    modified_body["model"] = str(modified_body["model"]).split("/")[-1]

            start_time = time.time()
            response = requests.post(target_url, headers=headers, json=modified_body, timeout=60)
            duration = time.time() - start_time

            if response.status_code == 200:
                pm.log("DEBUG", f"Request successful via {provider} ({duration:.2f}s)")
                return response.json()

            pm.log("WARN", f"Key failure on {provider} (Status {response.status_code}). Rotating...")
            last_error = f"Status {response.status_code}: {response.text}"

        except Exception as e:
            pm.log("ERROR", f"Request exception on {provider}: {str(e)}")
            last_error = str(e)
            continue

    pm.log("CRITICAL", f"All key rotation attempts failed for {provider}. Last error: {last_error}")
    raise HTTPException(status_code=500, detail=f"Neural failure: Details: {last_error}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
