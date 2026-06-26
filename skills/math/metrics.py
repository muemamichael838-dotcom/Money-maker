import math

def calculate_ev(win_prob, win_amount, lose_amount):
    """Calculate Expected Value (EV)."""
    return (win_prob * win_amount) - ((1 - win_prob) * lose_amount)

def kelly_criterion(win_prob, odds):
    """Calculate Kelly Criterion stake sizing."""
    if odds <= 1: return 0
    b = odds - 1
    p = win_prob
    q = 1 - p
    f = (b * p - q) / b
    return max(0, f)

def sharpe_ratio(returns, risk_free_rate=0.0):
    """Calculate the Sharpe Ratio."""
    if len(returns) < 2: return 0
    avg_return = sum(returns) / len(returns)
    variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
    std_return = math.sqrt(variance)
    if std_return == 0: return 0
    return (avg_return - risk_free_rate) / std_return

def sortino_ratio(returns, risk_free_rate=0.0, target_return=0.0):
    """Calculate the Sortino Ratio."""
    if len(returns) < 2: return 0
    avg_return = sum(returns) / len(returns)
    downside_returns = [r for r in returns if r < target_return]
    if not downside_returns: return 0
    downside_variance = sum((r - avg_return) ** 2 for r in downside_returns) / len(returns)
    downside_std = math.sqrt(downside_variance)
    if downside_std == 0: return 0
    return (avg_return - risk_free_rate) / downside_std

def max_drawdown(wealth_history):
    """Calculate the Maximum Drawdown."""
    if not wealth_history: return 0
    max_dd = 0
    peak = wealth_history[0]
    for value in wealth_history:
        if value > peak:
            peak = value
        dd = (value - peak) / peak
        if dd < max_dd:
            max_dd = dd
    return max_dd
