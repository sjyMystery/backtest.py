from ai.gp import PolicyGradient
from engine import Trade
from engine import BasicStratgy
import datetime
import numpy as np

class AIStrategy(BasicStratgy):
    def __init__(self):
        self.in_price = 0.0
        self.RL = PolicyGradient(
            2,10
        )
    def get_state(self,bin,ctx):
        return np.array([bin.ask_low,bin.ask_high,bin.ask_close,bin.ask_high,\
            bin.bid_low,bin.bid_high,bin.bid_open,bin.bid_high,\
            ctx.account.amounts,ctx.account.currency])
    def make_trade(self,bin,trust_trade,ctx):
        '''
            bins: 当前时刻的所有交易信息
            ctx: 交易的上下文信息（包含过去的一些信息）
            returns: 期望执行的交易列表，应该是一个Trade对象的列表。
        '''

        state = self.get_state(bin,ctx)

        max_in = ctx.account.max_in(bin.ask_high)
        max_out = ctx.account.max_out()

        action = self.RL.choose_action(state,[max_in,max_out])[0]

        if(action[0]>10):
            trust_trade('in',amounts=action[0],price=bin.ask_high,expire_delta=datetime.timedelta(minutes=5))
        if(action[1]>10):
            trust_trade('out',amounts=action[1],price=bin.bid_low,expire_delta=datetime.timedelta(minutes=5))
    def handle_trade_result(self,trade,ctx):
        '''
            is_success : 1 : success 0 : failed -1 : pending.
        '''

        # print(f'[{ctx.current_date}]:trade{trade}account:{ctx.account}')

    def after_run(self, history_status, ctx):
        pass