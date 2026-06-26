import json
import os
from persistence_manager import PersistenceManager

def add_cron_job(name, interval_seconds, script_path):
    pm = PersistenceManager()
    cron_file = os.path.join(os.environ.get("MONEY_MAKER_HOME", "/opt/data"), "crons.json")
    crons = []
    if os.path.exists(cron_file):
        with open(cron_file, 'r') as f:
            crons = json.load(f)

    crons.append({
        "name": name,
        "interval": interval_seconds,
        "script": script_path,
        "last_run": 0
    })

    with open(cron_file, 'w') as f:
        json.dump(crons, f)

    pm.log("INFO", f"New cron created: {name}")
    return f"Cron job '{name}' scheduled successfully."

if __name__ == "__main__":
    print("Cron tool ready.")
