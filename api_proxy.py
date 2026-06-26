import os
import json
import random
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Map environment variables to pools
KEY_POOLS = {
    "groq": os.environ.get("GROQ_API_KEYS", "").split(","),
    "huggingface": os.environ.get("HUGGINGFACE_API_KEYS", "").split(","),
    "google": os.environ.get("GOOGLE_API_KEYS", "").split(","),
    "openai": os.environ.get("OPENAI_API_KEYS", "").split(","),
    "anthropic": os.environ.get("ANTHROPIC_API_KEYS", "").split(","),
}

# Clean empty strings
for provider in KEY_POOLS:
    KEY_POOLS[provider] = [k.strip() for k in KEY_POOLS[provider] if k.strip()]

# Provider Configuration
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
    if not KEY_POOLS.get(provider):
        # Fallback to single key if pool is empty
        val = os.environ.get(f"{provider.upper()}_API_KEY")
        return val if val else None

    key = KEY_POOLS[provider].pop(0)
    KEY_POOLS[provider].append(key)
    return key

@app.get("/")
@app.get("/health")
async def health():
    return {"status": "proxy_online", "providers": list(KEY_POOLS.keys())}

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
    pool = KEY_POOLS.get(provider, [])
    max_retries = max(len(pool), 1) + 1
    last_error = "Unknown error"

    for _ in range(max_retries):
        api_key = get_next_key(provider)
        if not api_key:
            last_error = f"No API key found for {provider}"
            continue

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

            last_error = f"Status {response.status_code}: {response.text}"
            print(f"Provider {provider} failed: {last_error}. Rotating...")

        except Exception as e:
            last_error = str(e)
            print(f"Request to {provider} failed: {e}. Rotating...")
            continue

    raise HTTPException(status_code=500, detail=f"All keys for {provider} failed. Last error: {last_error}")

if __name__ == "__main__":
    # Internal bind to 127.0.0.1 as start.sh expects
    uvicorn.run(app, host="127.0.0.1", port=8000)
