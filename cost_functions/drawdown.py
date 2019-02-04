import numpy as np

def drawdown(history_status,calculated,ctx):
    currency = np.array(history_status["currency"])
    amounts = np.array(history_status["amounts"])
    ask_low = np.array(history_status["ask_low"])
    total = currency + amounts * ask_low * (1-ctx["trade_cost"])
    first = total[0]
    return np.max(np.abs((total - first) / first))