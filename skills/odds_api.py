import os
import requests

def get_odds(sport='upcoming', regions='us', markets='h2h'):
    api_key = os.environ.get("ODDS_API_KEY")
    if not api_key:
        return "Error: ODDS_API_KEY not set"

    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    params = {
        'apiKey': api_key,
        'regions': regions,
        'markets': markets,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"

    return response.json()

if __name__ == "__main__":
    # Example usage
    print(get_odds())
