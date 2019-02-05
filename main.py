from database import *
from engine import TradeEngine,Trade,Bin
from evaluator import Evaluator
from ai import AIStrategy
import datetime
import numpy as np
 
import matplotlib.pyplot as plt

startegy = AIStrategy()

print('start fetching data...')

bins = Bin.fetch('USDJPY',from_date=datetime.datetime(2013,1,1,0,0,0),to_date=datetime.datetime(2013,1,2,0,0,0))
print('load complete.')

Engine = TradeEngine(strategy=startegy,historybins=bins,initialCurrency=100000.00,trade_cost=2.5/10000)

history_status = Engine.run_backtest()

lines = history_status.plot.line(subplots=True)

plt.show()

evaluator = Evaluator(history_status)
 

print(evaluator.calculate_cost())