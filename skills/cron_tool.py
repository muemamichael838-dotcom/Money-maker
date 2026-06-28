import json
import os
import time
from persistence_manager import PersistenceManager

pm = PersistenceManager()

def manage_cron(action="list", name=None, interval=3600, script=None):
    """
    Manages autonomous recurring tasks.
    Actions: add, remove, list
    """
    cron_file = os.path.join(os.environ.get("MONEY_MAKER_HOME", "/opt/data"), "crons.json")
    os.makedirs(os.path.dirname(cron_file), exist_ok=True)

    crons = []
    if os.path.exists(cron_file):
        try:
            with open(cron_file, 'r') as f:
                crons = json.load(f)
        except:
            crons = []

    if action == "add":
        if not name or not script: return "ERROR: Name and script path required."
        # Update existing or add new
        for c in crons:
            if c["name"] == name:
                c["interval"] = interval
                c["script"] = script
                break
        else:
            crons.append({"name": name, "interval": interval, "script": script, "last_run": 0})

        with open(cron_file, 'w') as f:
            json.dump(crons, f, indent=2)
        pm.log("INFO", f"Autonomous Task Scheduled: {name} (Every {interval}s)")
        return f"SUCCESS: Task '{name}' is now active."

    elif action == "remove":
        new_crons = [c for c in crons if c["name"] != name]
        with open(cron_file, 'w') as f:
            json.dump(new_crons, f, indent=2)
        return f"SUCCESS: Task '{name}' removed."

    return crons

if __name__ == "__main__":
    print(manage_cron("list"))
