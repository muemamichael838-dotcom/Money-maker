import os
import time
import requests

def keep_alive():
    # Use HF Space URL or Render URL or custom input
    url = os.environ.get("KEEP_ALIVE_URL") or os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        return

    print(f"Starting Keep-alive for {url}")
    while True:
        try:
            # Ping health endpoint to prevent sleep/hibernation
            res = requests.get(f"{url}/health", timeout=15)
            print(f"Keep-alive pulse: {res.status_code}")
        except Exception as e:
            print(f"Keep-alive missed: {e}")

        time.sleep(600) # 10 Minutes

if __name__ == "__main__":
    keep_alive()
