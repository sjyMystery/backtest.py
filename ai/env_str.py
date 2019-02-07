from ai.gp import DDPG
from engine import Trade
from engine import BasicStratgy
from queue import Queue
import datetime
import numpy as np


class AIStrategy(BasicStratgy):
    def __init__(self,memory_cap=320,train=True):
        self.in_price = 0.0
        self.memory_cap = memory_cap
        self.RL = DDPG(
            2, 10,a_bound=1.0,
            memory_cap=self.memory_cap
        )
        self.queue = Queue(1024)
        self.train = train
        self.width = 3

    def get_state(self, bin, ctx):
        return np.array([bin.ask_low, bin.ask_high, bin.ask_close, bin.ask_high,
                         bin.bid_low, bin.bid_high, bin.bid_open, bin.bid_high,
                         ctx.account.amounts, ctx.account.currency])

    def reset(self,train=False):
        self.train = train
        self.width = 3
        self.queue=Queue(1024)
    def make_trade(self, bin, trust_trade, ctx):
        '''
            bins: 当前时刻的所有交易信息
            ctx: 交易的上下文信息（包含过去的一些信息）
            returns: 期望执行的交易列表，应该是一个Trade对象的列表。
        '''

        if(len(ctx.histories) >=20):
            data=ctx.slice_df(-21,-1)
            min = data.loc[:,"ask_low"].max()
            max = data.loc[:,"bid_high"].min()
            # if (bin.bid_close <= max):
            #     trust_trade('out',amounts=ctx.account.max_out(),price=bin.bid_close,expire_delta=datetime.timedelta(hours=1))
            if(bin.ask_close >= min):
                trust_trade('in',amounts=ctx.account.max_in(bin.ask_close),price=bin.ask_close,expire_delta=datetime.timedelta(hours=1))
        # state = self.get_state(bin, ctx)

        # max_in = ctx.account.max_in(bin.ask_high)
        # max_out = ctx.account.max_out()

        # action = self.RL.choose_action(state)

        # if(self.train):
        #     action = (np.random.normal(action,self.width)+self.width )/self.width
        #     self.queue.put((state,action))

            

        # trust_trade('in',amounts=max_in,price=bin.ask_high,expire_delta=datetime.timedelta(hours=5))
        # trust_trade('out',amounts=max_out,price=bin.bid_low,expire_delta=datetime.timedelta(hours=5))

    def handle_trade_result(self, trade, ctx):

        pass

    def after_trade(self, bin, ctx):

        # if self.train:
        #     assets = ctx.account.currency + ctx.account.amounts * \
        #         (bin.bid_low)*(1-ctx.account.trade_cost)
        #     reward = assets - ctx.account.start_cur
        #     state,action = self.queue.get()
        #     state_ = self.get_state(bin,ctx)

        #     self.RL.store_transition(s=state,a=action,r=reward,s_=state_)

        #     if self.RL.pointer > self.memory_cap:
        #             self.width *= 0.999995
        #             self.RL.learn()

        #     self.queue.task_done()
        pass

    def after_run(self, history_status, ctx):
        pass
