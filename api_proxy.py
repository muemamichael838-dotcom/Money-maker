import os
import json
import random
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

def get_pools():
    # Supports both singular (comma separated) and plural env vars
    pools = {
        "groq": (os.environ.get("GROQ_API_KEYS") or os.environ.get("GROQ_API_KEY") or "").split(","),
        "huggingface": (os.environ.get("HUGGINGFACE_API_KEYS") or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY") or "").split(","),
        "google": (os.environ.get("GOOGLE_API_KEYS") or os.environ.get("GOOGLE_API_KEY") or "").split(","),
        "openai": (os.environ.get("OPENAI_API_KEYS") or os.environ.get("OPENAI_API_KEY") or "").split(","),
        "anthropic": (os.environ.get("ANTHROPIC_API_KEYS") or os.environ.get("ANTHROPIC_API_KEY") or "").split(","),
    }
    # Clean and filter
    for p in pools:
        pools[p] = [k.strip() for k in pools[p] if k.strip()]
    return pools

KEY_POOLS = get_pools()

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
    },
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "header_type": "x-api-key"
    }
}

def get_next_key(provider):
    # Refresh pools to pick up live env changes if any
    pools = get_pools()
    pool = pools.get(provider, [])
    if not pool:
        return None
    # We rotate using a simple global index or just random for now to handle statelessness better
    return random.choice(pool)

@app.get("/")
@app.get("/health")
async def health():
    pools = get_pools()
    return {"status": "proxy_online", "active_providers": {p: len(v) for p, v in pools.items() if v}}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model = body.get("model", "").lower()

    provider = "openai"
    if "groq" in model: provider = "groq"
    elif "huggingface" in model or "hf" in model: provider = "huggingface"
    elif "google" in model or "gemini" in model: provider = "google"
    elif "claude" in model: provider = "anthropic"

    config = PROVIDERS.get(provider)
    if not config:
        raise HTTPException(status_code=400, detail=f"Unsupported provider for model: {model}")

    target_url = config["url"]
    if "{model}" in target_url:
        target_url = target_url.format(model=body.get("model"))

    # Determine retry count based on pool size
    pool = get_pools().get(provider, [])
    max_retries = max(len(pool), 3) # At least 3 retries
    last_error = "Unknown error"

    # Keep track of used keys in this request to avoid immediate reuse on failure
    tried_keys = set()

    for _ in range(max_retries):
        api_key = get_next_key(provider)
        if not api_key:
            last_error = f"No API key found for {provider}"
            break

        if api_key in tried_keys and len(tried_keys) < len(pool):
            continue

        tried_keys.add(api_key)

        headers = {"Content-Type": "application/json"}
        if config["header_type"] == "Bearer":
            headers["Authorization"] = f"Bearer {api_key}"
        else:
            headers[config["header_type"]] = api_key
            if provider == "anthropic":
                headers["anthropic-version"] = "2023-06-01"

        try:
            response = requests.post(
                target_url,
                headers=headers,
                json=body,
                timeout=60
            )

            if response.status_code == 200:
                return response.json()

            # Handle rate limits or key errors
            last_error = f"Status {response.status_code}: {response.text}"
            print(f"Provider {provider} failed with {response.status_code}. Rotating...")

        except Exception as e:
            last_error = str(e)
            print(f"Request to {provider} failed: {e}. Rotating...")
            continue

    raise HTTPException(status_code=500, detail=f"All keys for {provider} failed. Last error: {last_error}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
