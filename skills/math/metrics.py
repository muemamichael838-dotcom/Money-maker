import numpy as np

def calculate_ev(win_prob, win_amount, lose_amount):
    """Calculate Expected Value (EV)."""
    return (win_prob * win_amount) - ((1 - win_prob) * lose_amount)

def kelly_criterion(win_prob, odds):
    """Calculate Kelly Criterion stake sizing.
    odds is decimal odds (e.g., 2.0 for even money).
    """
    b = odds - 1
    p = win_prob
    q = 1 - p
    f = (b * p - q) / b
    return max(0, f)

def sharpe_ratio(returns, risk_free_rate=0.0):
    """Calculate the Sharpe Ratio."""
    if len(returns) < 2: return 0
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    if std_return == 0: return 0
    return (avg_return - risk_free_rate) / std_return

def sortino_ratio(returns, risk_free_rate=0.0, target_return=0.0):
    """Calculate the Sortino Ratio."""
    if len(returns) < 2: return 0
    avg_return = np.mean(returns)
    downside_returns = [r for r in returns if r < target_return]
    if not downside_returns: return 0
    downside_std = np.std(downside_returns)
    if downside_std == 0: return 0
    return (avg_return - risk_free_rate) / downside_std

def max_drawdown(wealth_history):
    """Calculate the Maximum Drawdown."""
    if not wealth_history: return 0
    wealth_history = np.array(wealth_history)
    peak = np.maximum.accumulate(wealth_history)
    drawdown = (wealth_history - peak) / peak
    return np.min(drawdown)
