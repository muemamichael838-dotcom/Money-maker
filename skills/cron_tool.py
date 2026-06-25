import os
import json
from persistence_manager import PersistenceManager

pm = PersistenceManager()

def add_cron_job(name, interval_minutes, task_description):
    """
    Registers a new autonomous task for the Money Maker orchestrator.
    The orchestrator runs in cron_manager.py.
    """
    jobs = pm.get_memory("autonomous_crons") or {}
    jobs[name] = {
        "interval": interval_minutes,
        "description": task_description,
        "status": "enabled"
    }
    pm.save_memory("autonomous_crons", jobs)
    pm.log("INFO", f"Autonomous Cron Added: {name} every {interval_minutes}m")
    return f"Job '{name}' has been scheduled."

def list_cron_jobs():
    """Returns all active autonomous cron jobs."""
    return pm.get_memory("autonomous_crons") or {}

if __name__ == "__main__":
    print(add_cron_job("Check BTC", 30, "Check bitcoin price and alert if > 100k"))
