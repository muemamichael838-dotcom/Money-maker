import os
import time
import schedule
from persistence_manager import PersistenceManager
from skills.odds_api import get_odds

pm = PersistenceManager()

def job_fetch_odds():
    pm.log("INFO", "Executing scheduled task: Fetch Odds")
    odds = get_odds()
    pm.save_memory("latest_odds", odds)
    pm.log("INFO", "Scheduled task complete: Fetch Odds")

def run_scheduler():
    pm.log("INFO", "Cron Manager started")
    # Fetch odds every 30 minutes
    schedule.every(30).minutes.do(job_fetch_odds)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
