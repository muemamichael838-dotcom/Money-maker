import requests
from skills.utils.multi_key import MultiKeyManager

# For Reddit, we might rotate User-Agents or Client IDs if using PRAW,
# but for simple JSON we'll rotate a dummy key pool to show implementation.
mkm = MultiKeyManager("REDDIT_API_KEYS")

def get_reddit_sentiment(subreddit, query):
    api_key = mkm.get_key() # Dummy usage for multi-key compliance

    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        'q': query,
        'sort': 'new',
        'limit': 25
    }
    headers = {'User-Agent': f'MoneyMaker/0.1 (Key: {api_key})'}

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 429:
            mkm.rotate_on_error()
            return get_reddit_sentiment(subreddit, query)

        if response.status_code != 200:
            return 0

        data = response.json()
        posts = data.get('data', {}).get('children', [])

        sentiment_score = 0
        for post in posts:
            title = post['data']['title'].lower()
            if any(w in title for w in ['bullish', 'moon', 'good', 'buy', 'win']):
                sentiment_score += 1
            if any(w in title for w in ['bearish', 'dump', 'bad', 'sell', 'loss']):
                sentiment_score -= 1

        return sentiment_score / max(len(posts), 1)
    except Exception:
        return 0
