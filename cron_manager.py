import os
import time
import schedule
import importlib.util
from persistence_manager import PersistenceManager

pm = PersistenceManager()

def run_autonomous_jobs():
    jobs = pm.get_memory("autonomous_crons") or {}
    for name, config in jobs.items():
        if config.get("status") == "enabled":
            # In a real implementation, we would use something like 'exec' or dynamic imports
            # For this agent, we log the intent to run the autonomous task.
            pm.log("INFO", f"Autonomous Job Triggered: {name} ({config.get('description')})")

def run_scheduler():
    pm.log("INFO", "Money Maker 🤑 Orchestrator started")

    # Static Jobs
    schedule.every(10).minutes.do(run_autonomous_jobs)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            pm.log("ERROR", f"Scheduler error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    run_scheduler()
