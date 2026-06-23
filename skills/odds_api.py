import os
import requests
from skills.utils.multi_key import MultiKeyManager

mkm = MultiKeyManager("ODDS_API_KEYS")

def get_odds(sport='upcoming', regions='us', markets='h2h'):
    api_key = mkm.get_key()
    if not api_key:
        return "Error: ODDS_API_KEY not set"

    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    params = {
        'apiKey': api_key,
        'regions': regions,
        'markets': markets,
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 429: # Rate limit
            mkm.rotate_on_error()
            return get_odds(sport, regions, markets)

        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"

        return response.json()
    except Exception as e:
        return f"Request failed: {e}"

if __name__ == "__main__":
    print(get_odds())
