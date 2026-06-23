import os
import time
import schedule
from persistence_manager import PersistenceManager
from skills.odds_api import get_odds
from skills.analysis.reddit_sentiment import get_reddit_sentiment
from skills.analysis.text_splitter import TextSplitter
from skills.finance.risk_manager import RiskManager
from skills.reasoning.decision_engine import DecisionEngine

pm = PersistenceManager()
ts = TextSplitter(chunk_size=3000)
rm = RiskManager(bankroll=1000)
de = DecisionEngine(pm)

def job_market_scan():
    pm.log("INFO", "Market Scan: Starting...")

    # Get Odds
    odds = get_odds()

    # Get Sentiment
    sentiment = get_reddit_sentiment("crypto", "BTC")

    # Analysis logic...
    pm.log("INFO", f"Market Scan: BTC Sentiment is {sentiment}")
    pm.log("INFO", "Market Scan: Complete.")

def job_data_cleanup():
    # Optimization for small servers
    pm.log("INFO", "Small Server Optimization: Cleaning logs...")
    # SQL to delete old logs...
    pass

def run_scheduler():
    pm.log("INFO", "MarketInsights-AI Orchestrator started")
    schedule.every(60).minutes.do(job_market_scan)
    schedule.every(24).hours.do(job_data_cleanup)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
