from bin import Bin
from database import *
from engine import TradeEngine
from evaluator import Evaluator
from trade import Trade
import datetime
import numpy as np 

print('start fetching data...')

result = Bin.fetch('AUDCAD',from_date=datetime.datetime(2012,1,1,0,0,0),to_date=datetime.datetime(2012,12,1,0,0,0))

print('load complete.')

class BasicStrategy:
    def __init__(self):
        pass

    def make_trade(self,bin,ctx):
        '''
            bins: 当前时刻的所有交易信息
            ctx: 交易的上下文信息（包含过去的一些信息）
            returns: 期望执行的交易列表，应该是一个Trade对象的列表。
        '''

        trades = []

        if len(ctx.histories) >= 20:

            data = ctx.slice_df(-21,-1)
            min = data.loc[:,"ask_low"].min()
            max = data.loc[:,"bid_high"].max()

            if(bin.ask_low <= min):
                trades.append(Trade('limit','in',ctx.account.max_in(bin.ask_low),bin.ask_low))
            if(bin.bid_high >= max):
                trades.append(Trade('limit','out',ctx.account.max_out(),bin.bid_high))
        return trades
    def valid_callback(self,valid,invalid):
        '''
           这里会告诉你哪些单子是有效被挂上了的
        '''
    def handle_trade(self,trade,is_success):
        '''
            is_success : 1 : success 0 : failed -1 : pending.
        '''
        pass


my_strategy = BasicStrategy()

Engine = TradeEngine(my_strategy,historybins=result,initialCurrency=100000.00,trade_cost=2.5/10000)

history_status = Engine.run_backtest()

evaluator = Evaluator(history_status=history_status,trade_cost=2.5/10000)


print(evaluator.calculate_cost())