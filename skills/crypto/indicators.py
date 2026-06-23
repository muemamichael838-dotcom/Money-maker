import numpy as np

def moving_average(data, window):
    if len(data) < window: return []
    return np.convolve(data, np.ones(window), 'valid') / window

def exponential_moving_average(data, window):
    if len(data) < window: return []
    alpha = 2 / (window + 1)
    ema = [data[0]]
    for i in range(1, len(data)):
        ema.append(data[i] * alpha + ema[-1] * (1 - alpha))
    return ema

def rsi(data, window=14):
    if len(data) < window + 1: return 50
    deltas = np.diff(data)
    seed = deltas[:window]
    up = seed[seed >= 0].sum() / window
    down = -seed[seed < 0].sum() / window
    rs = up / down if down != 0 else 100
    rsi = [100 - 100 / (1 + rs)]

    for i in range(window, len(deltas)):
        delta = deltas[i]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (window - 1) + upval) / window
        down = (down * (window - 1) + downval) / window
        rs = up / down if down != 0 else 100
        rsi.append(100 - 100 / (1 + rs))
    return rsi

def macd(data, slow=26, fast=12, signal=9):
    ema_fast = exponential_moving_average(data, fast)
    ema_slow = exponential_moving_average(data, slow)
    # Align lengths
    min_len = min(len(ema_fast), len(ema_slow))
    macd_line = np.array(ema_fast[-min_len:]) - np.array(ema_slow[-min_len:])
    signal_line = exponential_moving_average(macd_line, signal)
    return macd_line, signal_line

def bollinger_bands(data, window=20, num_std=2):
    ma = moving_average(data, window)
    std = [np.std(data[i:i+window]) for i in range(len(data)-window+1)]
    upper = np.array(ma) + num_std * np.array(std)
    lower = np.array(ma) - num_std * np.array(std)
    return upper, ma, lower
