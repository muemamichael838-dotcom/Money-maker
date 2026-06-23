import os
import time
import schedule
from persistence_manager import PersistenceManager
from skills.betting.analysis import detect_arbitrage, detect_value_bet
from skills.finance.risk_manager import RiskManager
from skills.reasoning.decision_engine import DecisionEngine
from skills.analysis.self_improvement import SelfImprovement
from skills.odds_api import get_odds

pm = PersistenceManager()
rm = RiskManager(bankroll=10000) # Initial bankroll
de = DecisionEngine(pm)
si = SelfImprovement(pm)

def job_market_scan():
    pm.log("INFO", "Market Scan: Starting...")
    odds_data = get_odds()
    # Process odds for value bets
    # This is a simplified loop
    if isinstance(odds_data, list):
        for match in odds_data:
            # logic to find value bets...
            pass

    pm.log("INFO", "Market Scan: Complete.")

def job_performance_report():
    pm.log("INFO", "Generating Performance Report...")
    history = pm.get_memory("perf_history") or []
    if history:
        wins = sum(1 for h in history if h["win"])
        win_rate = (wins / len(history)) * 100
        pm.log("REPORT", f"Win Rate: {win_rate:.2f}% | Sample: {len(history)}")

    si.analyze_mistakes()

def run_scheduler():
    pm.log("INFO", "Money Maker Orchestrator started")

    # Schedule tasks
    schedule.every(15).minutes.do(job_market_scan)
    schedule.every(24).hours.do(job_performance_report)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            pm.log("ERROR", f"Scheduler error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
