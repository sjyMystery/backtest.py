import numpy as np
from pandas import DataFrame
from engine.engine import Context
def drawdown(history_status:DataFrame,calculated:dict,ctx:Context):
    currency = np.array(history_status["currency"])
    amounts = np.array(history_status["amounts"])
    ask_low = np.array(history_status["ask_low"])
    total = currency + amounts * ask_low * (1-ctx.account.trade_cost)
    first = total[0]
    return np.max((np.zeros(total.shape)-total +first) / first)