import os
import requests

def deploy_proxy_worker():
    token = os.environ.get("CLOUDFLARE_WORKERS_TOKEN")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    target_url = os.environ.get("SPACE_URL") # Hugging Face Space URL

    if not all([token, account_id, target_url]):
        print("Cloudflare credentials or SPACE_URL missing. Skipping deployment.")
        return

    script_content = f"""
    addEventListener('fetch', event => {{
      event.respondWith(handleRequest(event.request))
    }})

    async function handleRequest(request) {{
      const url = new URL(request.url)
      url.hostname = '{target_url.replace("https://", "").replace("http://", "").split("/")[0]}'

      const newRequest = new Request(url, {{
        method: request.method,
        headers: request.headers,
        body: request.body
      }})

      return fetch(newRequest)
    }}
    """

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/money-maker-proxy"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/javascript"
    }

    try:
        resp = requests.put(url, data=script_content, headers=headers)
        if resp.status_code == 200:
            print("Cloudflare Proxy Worker deployed successfully.")
        else:
            print(f"Cloudflare deployment failed: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deploy_proxy_worker()
