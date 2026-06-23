import os
import requests
import time
from bs4 import BeautifulSoup
from apify_client import ApifyClient

def scrape_url(url, use_apify=False):
    # Politeness delay
    time.sleep(2)

    if use_apify:
        client = ApifyClient(os.environ.get("APIFY_TOKEN"))
        run_input = { "startUrls": [{ "url": url }] }
        run = client.actor("apify/web-scraper-smart").call(run_input=run_input)
        return list(client.dataset(run["defaultDatasetId"]).iterate_items())

    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'MarketInsights/0.1'})
        soup = BeautifulSoup(response.content, 'html.parser')
        return {
            "title": soup.title.string if soup.title else "",
            "text": soup.get_text()[:5000]
        }
    except Exception as e:
        return f"Scraping failed: {e}"
