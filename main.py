from bin import Bin
from database import *
from engine import TradeEngine
import datetime


result = Bin.fetch('AUDCAD',from_date=datetime.datetime(2012,1,1,0,0,0),to_date=datetime.datetime(2012,1,5,0,0,0))

class BasicStrategy:
    def __init__(self):
        pass

    def make_trade(self,bin,ctx):
        '''
            bins: 当前时刻的所有交易信息
            ctx: 交易的上下文信息（包含过去的一些信息）
            returns: 期望执行的交易列表，应该是一个Trade对象的列表。
        '''
        print(bin.ask_low)

        return []
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

Engine = TradeEngine(my_strategy,historybins=result,initialCurrency=100000.00)

result = Engine.run_backtest()

print(result)