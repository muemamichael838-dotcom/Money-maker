import os
import time
import requests

def keep_alive():
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        # Fallback to current host if possible or skip
        return

    print(f"Starting Render keep-alive for {url}")
    while True:
        try:
            # Ping every 10 minutes to stay awake on free tier
            res = requests.get(f"{url}/health", timeout=10)
            print(f"Keep-alive ping: {res.status_code}")
        except Exception as e:
            print(f"Keep-alive failed: {e}")

        time.sleep(600)

if __name__ == "__main__":
    keep_alive()
