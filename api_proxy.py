import os
import json
import random
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import litellm
from litellm import completion

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

def get_next_key(provider):
    if not KEY_POOLS.get(provider):
        return os.environ.get(f"{provider.upper()}_API_KEY")
    key = KEY_POOLS[provider].pop(0)
    KEY_POOLS[provider].append(key)
    return key

@app.get("/")
@app.get("/health")
async def health():
    return {"status": "proxy_online"}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    model = body.get("model", "")

    provider = "openai"
    if "groq" in model: provider = "groq"
    elif "huggingface" in model or "hf" in model: provider = "huggingface"
    elif "google" in model or "gemini" in model: provider = "google"
    elif "claude" in model: provider = "anthropic"

    max_retries = len(KEY_POOLS.get(provider, [1])) + 1
    last_exception = None

    for _ in range(max_retries):
        api_key = get_next_key(provider)
        try:
            response = completion(
                **body,
                api_key=api_key
            )
            return response
        except Exception as e:
            last_exception = e
            print(f"Error with {provider} key: {e}. Rotating...")
            continue

    raise HTTPException(status_code=500, detail=str(last_exception))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
