from skills.math.metrics import kelly_criterion

class RiskManager:
    def __init__(self, bankroll, max_drawdown_limit=0.2, daily_loss_limit=0.05):
        self.bankroll = bankroll
        self.max_drawdown_limit = max_drawdown_limit
        self.daily_loss_limit = daily_loss_limit
        self.daily_starting_bankroll = bankroll
        self.current_drawdown = 0

    def check_limits(self, current_bankroll):
        self.bankroll = current_bankroll
        daily_loss = (self.daily_starting_bankroll - self.bankroll) / self.daily_starting_bankroll

        if daily_loss >= self.daily_loss_limit:
            return False, "Daily loss limit reached"

        if self.current_drawdown >= self.max_drawdown_limit:
            return False, "Maximum drawdown limit reached"

        return True, "Safe"

    def calculate_stake(self, win_prob, odds, fraction=0.5):
        """Calculate recommended stake using Fractional Kelly."""
        kelly_f = kelly_criterion(win_prob, odds)
        stake = self.bankroll * kelly_f * fraction
        return max(0, stake)

    def validate_trade(self, ev, confidence):
        if ev <= 0:
            return False, "Negative EV"
        if confidence < 0.6:
            return False, "Low confidence"
        return True, "Validated"

if __name__ == "__main__":
    rm = RiskManager(1000)
    print(rm.calculate_stake(0.6, 2.0))
