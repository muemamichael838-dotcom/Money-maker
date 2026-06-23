def detect_arbitrage(odds_list):
    """Detect arbitrage opportunities.
    odds_list: list of decimal odds from different bookies for all outcomes.
    e.g., [2.1, 2.0] for a 2-outcome event.
    """
    implied_sum = sum(1/o for o in odds_list)
    if implied_sum < 1.0:
        profit_pct = (1 - implied_sum) * 100
        return True, profit_pct
    return False, 0

def calculate_clv(placed_odds, closing_odds):
    """Calculate Closing Line Value (CLV)."""
    return (placed_odds / closing_odds - 1) * 100

def detect_value_bet(estimated_prob, market_odds):
    """Identify if a bet has value (Positive EV)."""
    implied_prob = 1 / market_odds
    if estimated_prob > implied_prob:
        edge = (estimated_prob - implied_prob) / implied_prob
        return True, edge
    return False, 0

def detect_line_movement(history):
    """Detect sharp line movement."""
    if len(history) < 2: return 0
    return history[-1] - history[0]
