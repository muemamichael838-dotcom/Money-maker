import os
import requests
from persistence_manager import PersistenceManager

class ApifyTool:
    def __init__(self):
        self.token = os.environ.get("APIFY_TOKEN")
        self.pm = PersistenceManager()

    def run_actor(self, actor_id, input_data):
        if not self.token:
            return {"error": "APIFY_TOKEN not set"}

        url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={self.token}"
        try:
            resp = requests.post(url, json=input_data)
            if resp.status_code == 201:
                run_id = resp.json()["data"]["id"]
                self.pm.log("INFO", f"Apify Actor {actor_id} started: {run_id}")
                return {"run_id": run_id, "status": "started"}
            return {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    tool = ApifyTool()
    print("Apify Tool Loaded.")
