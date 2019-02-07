from database import *
from engine import TradeEngine,Trade,Bin
from evaluator import Evaluator
from ai import AIStrategy
import datetime
import numpy as np
 



def main():
    startegy = AIStrategy()

    print('start fetching data...')

    bins = Bin.fetch('USDJPY',from_date=datetime.datetime(2018,3,13,0,0,0),to_date=datetime.datetime(2018,3,17,0,0,0))
    print('load complete. total : %d' % (len(bins)))
    Engine = TradeEngine(strategy=startegy,historybins=bins,initialCurrency=1000000.00,trade_cost=2.5/(1e+6))

    history_status,ctx = Engine.run_backtest()
    evaluator = Evaluator(history_status,ctx)
    print('start evaluate')
    evaluator.run()

if __name__ == "__main__":
    main()
# bins = Bin.fetch('USDJPY',from_date=datetime.datetime(2018,1,1,0,0,0),to_date=datetime.datetime(2018,1,1,0,15,0))

# startegy.reset()

# Engine = TradeEngine(strategy=startegy,historybins=bins,initialCurrency=100000.00,trade_cost=2.5/(1e+6))
# history_status = Engine.run_backtest()

# lines = history_status.plot.line(subplots=True)
