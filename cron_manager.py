import os
import time
import importlib.util
from persistence_manager import PersistenceManager

pm = PersistenceManager()

def run_autonomous_jobs():
    jobs = pm.get_memory("autonomous_crons") or {}
    for name, config in jobs.items():
        if config.get("status") == "enabled":
            pm.log("INFO", f"Autonomous Job Triggered: {name} ({config.get('description')})")

def run_scheduler():
    pm.log("INFO", "Money Maker 🤑 Orchestrator started")

    last_run = 0
    while True:
        try:
            now = time.time()
            if now - last_run > 600: # Every 10 minutes
                run_autonomous_jobs()
                last_run = now
        except Exception as e:
            pm.log("ERROR", f"Scheduler error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    run_scheduler()
