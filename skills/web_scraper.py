import os
import requests
from bs4 import BeautifulSoup
from apify_client import ApifyClient

def scrape_url(url, use_apify=False):
    if use_apify:
        client = ApifyClient(os.environ.get("APIFY_TOKEN"))
        run_input = { "startUrls": [{ "url": url }] }
        run = client.actor("apify/web-scraper-smart").call(run_input=run_input)
        return list(client.dataset(run["defaultDatasetId"]).iterate_items())

    # Redundant fallback
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        return {
            "title": soup.title.string if soup.title else "",
            "text": soup.get_text()[:5000] # Limit size
        }
    except Exception as e:
        return f"Scraping failed: {e}"

if __name__ == "__main__":
    print(scrape_url("https://example.com"))
