import os
import json

class SelfImprovement:
    def __init__(self, persistence_manager):
        self.pm = persistence_manager

    def track_performance(self, prediction, outcome):
        success = (prediction == outcome)
        self.pm.log("PERFORMANCE", f"Prediction: {prediction} | Outcome: {outcome} | Result: {'WIN' if success else 'LOSS'}")

        # Save to memory for pattern detection
        history = self.pm.get_memory("perf_history") or []
        history.append({"pred": prediction, "out": outcome, "win": success})
        self.pm.save_memory("perf_history", history[-1000:]) # Keep last 1000

    def analyze_mistakes(self):
        history = self.pm.get_memory("perf_history") or []
        losses = [h for h in history if not h["win"]]
        if len(losses) > 5:
            # Simple placeholder for pattern detection
            self.pm.log("ALERT", "Recurring mistake patterns detected. Consider retraining model.")
            return True
        return False

    def trigger_retraining(self):
        self.pm.log("INFO", "Self-Improvement: Triggering model retraining...")
        # In a real scenario, this would call a training script
        return True

if __name__ == "__main__":
    from persistence_manager import PersistenceManager
    pm = PersistenceManager()
    si = SelfImprovement(pm)
    si.track_performance("Team A wins", "Team B wins")
