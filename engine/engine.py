from pandas import DataFrame
import numpy as np
from engine.basic_strategy import BasicStratgy
from engine.account import Account
from engine.trade import Trade
import datetime
import tensorflow as tf


class Context:

    current_date : datetime.datetime

    def __init__(self,account,histories,current_date=None):
        self.account = account
        self.histories = histories
        self.current_date = current_date
        self.made_trades = []
    def slice_df(self,start,end):
        sliced = self.histories[start:end]
        [date,history] = list(zip(*sliced))
        return DataFrame(data=history,index=date)

    def made_trade(self,trade):
        self.made_trades.append(trade)
class TradeEngine:
    
    pending_trades = []

    history_status = DataFrame(columns=["ask_low","ask_high","ask_open","ask_close",\
        "bid_low","bid_high","bid_open","bid_close",
        "currency","amounts","date"])

    def __init__(self,strategy:BasicStratgy,historybins,initialCurrency,trade_cost=0.00025):
        '''
            startegy: 策略对象实例。
            historybins: tf.Tensor的一个实例，它的形状为(bin中时间序列总长度）
            cost_function_list
        '''
        self.account = Account(initialCurrency,trade_cost)
        self.histories = []
        self.ctx = Context(self.account,self.histories)
        self.strategy = strategy
        self.historybins = historybins


    def reset(self):
        self.pending_trades.clear()
        # 清除所有历史记录
        self.histories.clear()





    def to_trust_trade(self,trade):
        '''
            处理策略给出的交易
            判断哪些是合法的交易
            哪些不是合法的交易
            再将交易入队列
            并且回调
        '''

        if trade.amounts >= 1e-3:
            can_trust = trade.to_trust()
            if can_trust: 
                self.pending_trades.append(trade)
            return can_trust
        return False

    def handle_trusted_trades(self,current_bin,next_bin):

        new_trades = []

        for trade in self.pending_trades:

            if trade.to_made(current_bin,next_bin):
                self.ctx.made_trade(trade)
                self.strategy.handle_trade_result(trade,self.ctx)
            else:
                new_trades.append(trade)

        return new_trades

    def trust_trade_generator(self,trust_date):
        '''
            make_trade_generator:
                给出当前时间，生成一个maker,该maker被调用之后直接受到委托
                参数：
                    -current_date: 当前时间
                
        '''
        def trust_trade(des,type='limit',amounts=0.0,price=0.0,expire_delta:datetime.timedelta=None):
            '''
                make_trade:
                以依赖注入的方式请求委托。
                    -des 标的 取 in 或者 out
                    -amounts 交易数量
                    -price 交易价格
                    -expire_delta 最长有效期
            '''
            trade = Trade(type=type,des=des,amounts=amounts,price=price,expire_delta=expire_delta,trust_date=trust_date,account=self.account)
            return self.to_trust_trade(trade)
        return trust_trade
    def run_backtest(self):

        bin_length = len(self.historybins)

        self.reset()


        # 一开始有一个历史……
        self.histories+=[self.make_status(self.historybins[0])]

        for i in range(bin_length-1):
            current_bin = self.historybins[i]
            next_bin = self.historybins[i+1]
            
            self.ctx.current_date = next_bin.start_date

            self.strategy.make_trade(current_bin,self.trust_trade_generator(self.ctx.current_date),self.ctx)


    #        print(f'[B][{next_bin.start_date}]{self.ctx.account}')

            self.pending_trades = self.handle_trusted_trades(current_bin,next_bin)

          #  print(f'[A][{next_bin.end_date}]{self.ctx.account}')

            status = self.make_status(next_bin)
            # update status
            self.histories+=[status]

            self.ctx.current_date = next_bin.end_date

            self.strategy.after_trade(next_bin,self.ctx)


            if(i%10000 is 0):
                print(f'{i+1}/{bin_length} done.')

        a= list(zip(*self.histories))

        self.history_status = DataFrame(a[1],index=a[0])
        
        self.strategy.after_run(self.history_status,self.ctx)

        return self.history_status,self.ctx

    def make_status(self,bin):
        return (bin.start_date,{
            "ask_low":bin.ask_low,
            "ask_high":bin.ask_high,
            "ask_open":bin.ask_open,
            "ask_close":bin.ask_close,
            "bid_low":bin.bid_low,
            "bid_high":bin.bid_high,
            "bid_open":bin.bid_open,
            "bid_close":bin.bid_close ,
            "currency":self.account.currency,
            "frozen_currency":self.account.frozen_cur,
            "amounts":self.account.amounts,
            "frozen_amounts":self.account.frozen_amo,
            "assets":self.account.assets(bin.bid_close),
        })
