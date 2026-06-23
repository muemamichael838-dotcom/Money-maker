class DecisionEngine:
    def __init__(self, persistence_manager):
        self.pm = persistence_manager

    def evaluate_opportunity(self, action_type, details, signals=None):
        """
        action_type: 'EXECUTE', 'DELETE_SKILL', 'UPDATE_CORE'
        details: description of the action
        """
        reasons = []
        confidence = 0

        # Human-in-the-loop for destructive actions
        destructive_actions = ['DELETE_SKILL', 'WIPE_MEMORY', 'UPDATE_CORE', 'EXECUTE_SHELL']
        if action_type in destructive_actions:
            self.pm.log("SAFETY", f"PAUSED: {action_type} requires human confirmation. Reason: {details}")
            return {
                "decision": "WAITING_FOR_USER",
                "explanation": f"This action ({action_type}) is marked as destructive. I need your explicit permission to proceed.",
                "confidence": 1.0
            }

        # Regular opportunity evaluation logic
        if signals:
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

        self.pm.log("DECISION", f"Action: {decision} | Confidence: {confidence} | Why: {explanation}")

        return {
            "decision": decision,
            "explanation": explanation,
            "confidence": confidence
        }
