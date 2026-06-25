import requests

def search_wikipedia(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query
    }
    response = requests.get(url, params=params)
    return response.json()

if __name__ == "__main__":
    print(search_wikipedia("Money Making Strategies"))
