import os
import requests
import time
import re

def scrape_website(url):
    """
    Ultra-lightweight web scraper using requests and regex.
    Zero external dependencies besides standard library.
    """
    print(f"Scraping {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Error: Status code {response.status_code}"

        html = response.text
        # Very crude text extraction
        text = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<.*?>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text[:5000]

    except Exception as e:
        return f"Scraping failed: {str(e)}"

def get_market_news():
    return scrape_website("https://www.reuters.com/markets/")

if __name__ == "__main__":
    print(get_market_news()[:500])
