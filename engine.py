from account import Account 
from pandas import DataFrame
from cost_functions import *

import tensorflow as tf


class Context:
    def __init__(self,account):
        self.account = account

class TradeEngine:

    trades=[]

    cost_functions = costs

    history_status=DataFrame(columns=['current_date','currency','amounts'])


    def __init__(self,strategy,historybins,initialCurrency,cost_functions_list=[]):
        '''
            startegy: 策略对象实例。
            historybins: tf.Tensor的一个实例，它的形状为(bin中时间序列总长度）

            cost_function_list
        '''
        self.account = Account(initialCurrency)
        self.ctx = Context(self.account)
        self.strategy = strategy
        self.historybins = historybins
        self.cost_functions += cost_functions_list

    def judge_trade(self,trade,current_bin,next_bin):
        '''
            计算是否达到成交条件
        '''
        if(trade.type == 'limit'):
            if trade.des == 'in':
                return trade.price >= current_bin.ask_low \
                    and trade.price < next_bin.ask_close 
            elif trade.des == 'out':
                return trade.price <= current_bin.bid_heigh \
                    and trade.price > next_bin.bid_close
                    # 卖出的时候，要求被卖的数量要多一些
        elif trade.type == 'market':
            return True
        else :
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
                if current_bin.end_date >= trade.expire_date:
                    self.account.trade_failed(trade)
                    self.strategy.handle_trade(trade,0)
                else:
                    new_trades.append(trade)
                    self.strategy.handle_trade(trade,-1)
        
        return new_trades

    def run_backtest(self):

        bin_length = len(self.historybins)

        for i in range(bin_length-1):
            current_bin = self.historybins[i]
            next_bin = self.historybins[i+1]
            
            requests = self.strategy.make_trade(current_bin,self.ctx)

            self.validate_requested_trades(requests)

            self.trades = self.handle_requested_trades(current_bin,next_bin)

            self.save_status(current_bin.end_date)


        return self.calculate_cost()

    def save_status(self,date):
        self.history_status.append({
          "date":date,
          "currency":self.account.currency,
          "amounts":self.account.amounts
        },ignore_index=True)
    
    def calculate_cost(self):


        with tf.variable_scope('calculate_cost'):
        
            history_status = tf.Variable(name='history_status')
            history_bins = tf.Variable(name='history_bins')
        
        with tf.Session() as sess:
            result_lists=sess.run([cost(history_status=history_status,bins=history_bin) for cost in self.cost_functions],{
                history_bin:self.historybins,
                history_status:self.history_status
            })
        
        return result_lists