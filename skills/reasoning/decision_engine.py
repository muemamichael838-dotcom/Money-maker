class DecisionEngine:
    def __init__(self, persistence_manager):
        self.pm = persistence_manager

    def evaluate_opportunity(self, signals, risk_profile):
        """
        signals: dict of signals from various modules.
        risk_profile: current risk settings.
        """
        reasons = []
        confidence = 0

        # Example logic
        if signals.get('ev', 0) > 0.05:
            reasons.append("High Positive EV detected")
            confidence += 0.4

        if signals.get('trend') == 'bullish':
            reasons.append("Technical trend is Bullish")
            confidence += 0.3

        if signals.get('sentiment', 0) > 0.6:
            reasons.append("Strong positive sentiment")
            confidence += 0.2

        explanation = "; ".join(reasons)

        decision = "EXECUTE" if confidence >= 0.7 else "REJECT"

        if decision == "REJECT":
            reasons.append("Insufficient confidence or signals")

        # Log decision reasoning
        self.pm.log("DECISION", f"Action: {decision} | Confidence: {confidence} | Why: {explanation}")

        return {
            "decision": decision,
            "explanation": explanation,
            "confidence": confidence
        }

    def confidence_check(self, data_quality_score):
        if data_quality_score < 0.5:
            return False, "Ask for clarification: Data quality is too low"
        return True, "Data quality OK"
