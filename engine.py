from account import Account 
from pandas import DataFrame
import numpy as np

import tensorflow as tf


class Context:
    def __init__(self,account,histories,current_date=None):
        self.account = account
        self.histories = histories
        self.current_date = current_date
    def slice_df(self,start,end):
        sliced = self.histories[start:end]
        [date,history] = list(zip(*sliced))
        return DataFrame(data=history,index=date)

class TradeEngine:
    
    trades = []

    history_status = DataFrame(columns=["ask_low","ask_high","ask_open","ask_close",\
        "bid_low","bid_high","bid_open","bid_close",
        "currency","amounts","date"])

    def __init__(self,strategy,historybins,initialCurrency,trade_cost=0.00025):
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


    def judge_trade(self,trade,current_bin,next_bin):
        '''
            计算是否达到成交条件
        '''
        if(trade.type == 'limit'):
            if trade.des == 'in':
                return trade.price >= current_bin.ask_low \
                    and trade.price < next_bin.ask_close 
            elif trade.des == 'out':
                return trade.price <= current_bin.bid_high \
                    and trade.price > next_bin.bid_close
                    # 卖出的时候，要求被卖的数量要多一些

        elif trade.type == 'market':
            return True
        else:
            return False




    def push_trade(self,trade):
        '''
            交易入列表，并且冻结相关资源余额
        '''
        self.account.trade_trust(trade)
        self.trades.append(trade)

    def validate_requested_trades(self,request_trades):
        '''
            处理策略给出的交易
            判断哪些是合法的交易
            哪些不是合法的交易
            再将交易入队列
            并且回调
        '''
        valid_trades = []
        invalid_trades = []

        for trade in request_trades:
            if self.account.trade_avaliable(trade):
                valid_trades.append(trade)
                self.push_trade(trade=trade)
            else:
                invalid_trades.append(trade)

        self.strategy.valid_callback(valid_trades,invalid_trades)

    def handle_requested_trades(self,current_bin,next_bin):

        new_trades = []

        for trade in self.trades:
            successful = self.judge_trade(trade,current_bin,next_bin)
            if successful:
                self.account.trade_success(trade)
                self.strategy.handle_trade(trade,1)
            else:
                if trade.expire_date is not None and current_bin.end_date >= trade.expire_date:
                    self.account.trade_failed(trade)
                    self.strategy.handle_trade(trade,0)
                else:
                    new_trades.append(trade)
                    self.strategy.handle_trade(trade,-1)
        
        return new_trades

    def run_backtest(self):
        print('backtest start')

        bin_length = len(self.historybins)

        # 清除所有历史记录
        self.histories.clear()

        # 一开始有一个历史……
        self.histories+=[self.make_status(self.historybins[0])]

        for i in range(bin_length-1):
            current_bin = self.historybins[i]
            next_bin = self.historybins[i+1]
            
            self.ctx.current_date = current_bin.end_date
            requests = self.strategy.make_trade(current_bin,self.ctx)

            self.validate_requested_trades(requests)

            self.trades = self.handle_requested_trades(current_bin,next_bin)


            # update status
            self.histories+=[self.make_status(next_bin)]

            if i % 10000 == 0 :
                print(f'{i}/{bin_length-1} bin done. End Date:{current_bin.end_date}')

        a= list(zip(*self.histories))

        self.history_status = DataFrame(a[1],index=a[0])

        return self.history_status

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
            "amounts":self.account.amounts,
        })
