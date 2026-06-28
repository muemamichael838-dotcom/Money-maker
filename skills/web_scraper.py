import requests
from bs4 import BeautifulSoup
import os
import json
from skills.utils.multi_key import MultiKeyManager

apify_mkm = MultiKeyManager("APIFY_API_KEYS")

def scrape_url(url, use_apify=False):
    """
    Scrapes a website. Fallback logic:
    1. Standard requests/BS4
    2. Apify (if requested or if standard fails)
    """
    if use_apify:
        return _scrape_with_apify(url)

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract main text
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return "\n".join(chunk for chunk in chunks if chunk)
        else:
            return _scrape_with_apify(url)
    except Exception:
        return _scrape_with_apify(url)

def _scrape_with_apify(url):
    api_key = apify_mkm.get_key()
    if not api_key:
        return "Error: No Apify API key found for industrial scraping."

    # Using Apify's Web Scraper or a simple content extractor actor
    # This is a simplified call to the Apify API
    actor_id = "aGmq9YmYSkYid7fXF" # Content Checker or similar
    api_url = f"https://api.apify.com/v2/acts/apify~web-scraper/run-sync-get-dataset-items?token={api_key}"

    payload = {
        "startUrls": [{"url": url}],
        "maxPagesPerCrawl": 1,
        "pageFunction": "async function pageFunction(context) { return { url: context.request.url, content: document.body.innerText }; }"
    }

    try:
        res = requests.post(api_url, json=payload, timeout=60)
        if res.status_code == 201 or res.status_code == 200:
            data = res.json()
            return data[0].get("content", "No content found via Apify.")
        return f"Apify failed with status {res.status_code}"
    except Exception as e:
        return f"Apify exception: {str(e)}"

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    print(scrape_url(target))
