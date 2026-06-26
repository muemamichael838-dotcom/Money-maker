import time
import os
import json
import subprocess
from persistence_manager import PersistenceManager

class CronManager:
    def __init__(self):
        self.pm = PersistenceManager()
        self.cron_file = os.path.join(os.environ.get("MONEY_MAKER_HOME", "/opt/data"), "crons.json")

    def run(self):
        self.pm.log("INFO", "Money Maker 🤑 Orchestrator started")
        while True:
            if os.path.exists(self.cron_file):
                try:
                    with open(self.cron_file, 'r') as f:
                        crons = json.load(f)

                    updated = False
                    now = time.time()
                    for cron in crons:
                        last_run = cron.get("last_run", 0)
                        interval = cron.get("interval", 3600)
                        if now - last_run >= interval:
                            self.pm.log("INFO", f"Executing scheduled task: {cron['name']}")
                            try:
                                subprocess.run(["python3", cron["script"]], check=False)
                            except Exception as e:
                                self.pm.log("ERROR", f"Task {cron['name']} failed: {e}")
                            cron["last_run"] = now
                            updated = True

                    if updated:
                        with open(self.cron_file, 'w') as f:
                            json.dump(crons, f)
                except Exception as e:
                    self.pm.log("ERROR", f"Cron loop error: {e}")
            else:
                # Initialize default crons
                default_crons = [
                    {"name": "Market Sync", "interval": 3600, "script": "skills/odds_api.py", "last_run": 0},
                    {"name": "HF Backup", "interval": 21600, "script": "skills/hf_backup.py", "last_run": 0}
                ]
                with open(self.cron_file, 'w') as f:
                    json.dump(default_crons, f)

            time.sleep(60) # Pulse every minute

if __name__ == "__main__":
    cm = CronManager()
    cm.run()
