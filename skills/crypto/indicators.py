import math

def moving_average(data, window):
    if len(data) < window: return []
    result = []
    for i in range(len(data) - window + 1):
        result.append(sum(data[i:i+window]) / window)
    return result

def exponential_moving_average(data, window):
    if not data or window <= 0: return []
    alpha = 2 / (window + 1)
    ema = [data[0]]
    for i in range(1, len(data)):
        ema.append(data[i] * alpha + ema[-1] * (1 - alpha))
    return ema

def rsi(data, window=14):
    if len(data) < window + 1: return [50]

    deltas = [data[i+1] - data[i] for i in range(len(data)-1)]
    up = [d if d > 0 else 0 for d in deltas]
    down = [-d if d < 0 else 0 for d in deltas]

    avg_gain = sum(up[:window]) / window
    avg_loss = sum(down[:window]) / window

    rsi_list = []
    if avg_loss == 0:
        rsi_list.append(100)
    else:
        rs = avg_gain / avg_loss
        rsi_list.append(100 - (100 / (1 + rs)))

    for i in range(window, len(deltas)):
        avg_gain = (avg_gain * (window - 1) + up[i]) / window
        avg_loss = (avg_loss * (window - 1) + down[i]) / window

        if avg_loss == 0:
            rsi_list.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi_list.append(100 - (100 / (1 + rs)))

    return rsi_list

def macd(data, slow=26, fast=12, signal=9):
    ema_fast = exponential_moving_average(data, fast)
    ema_slow = exponential_moving_average(data, slow)
    min_len = min(len(ema_fast), len(ema_slow))
    macd_line = [ema_fast[-min_len+i] - ema_slow[-min_len+i] for i in range(min_len)]
    signal_line = exponential_moving_average(macd_line, signal)
    return macd_line, signal_line

def bollinger_bands(data, window=20, num_std=2):
    ma = moving_average(data, window)
    std_devs = []
    for i in range(len(data) - window + 1):
        window_data = data[i:i+window]
        avg = sum(window_data) / window
        variance = sum((x - avg) ** 2 for x in window_data) / window
        std_devs.append(math.sqrt(variance))

    upper = [ma[i] + num_std * std_devs[i] for i in range(len(ma))]
    lower = [ma[i] - num_std * std_devs[i] for i in range(len(ma))]
    return upper, ma, lower
