import requests
from skills.utils.multi_key import MultiKeyManager
from persistence_manager import PersistenceManager

mkm = MultiKeyManager("ODDS_API_KEYS")
pm = PersistenceManager()

def get_live_odds(sport='upcoming', regions='us', markets='h2h'):
    """
    Retrieves live betting odds. Features:
    - Multi-key rotation on 429
    - Persistence logging for historical analysis
    """
    api_key = mkm.get_key()
    if not api_key:
        return "ERROR: No Odds API Key in pool. Set 'ODDS_API_KEYS' in settings."

    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    params = {
        'apiKey': api_key,
        'regions': regions,
        'markets': markets,
        'oddsFormat': 'decimal'
    }

    try:
        response = requests.get(url, params=params, timeout=15)

        if response.status_code == 429:
            pm.log("WARN", "Odds API Rate Limit Hit. Rotating Key.")
            # Recursive retry with key rotation (managed by mkm internally on next get_key)
            return get_live_odds(sport, regions, markets)

        if response.status_code != 200:
            return f"ERROR: Odds API responded with {response.status_code}: {response.text}"

        data = response.json()
        pm.log("INFO", f"Fetched odds for {len(data)} events in {sport}.")
        return data

    except Exception as e:
        pm.log("ERROR", f"Odds API Request Failed: {str(e)}")
        return f"ERROR: Connection failure - {str(e)}"

if __name__ == "__main__":
    # Test with dummy/empty key
    print(get_live_odds())
