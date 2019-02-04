from account import Account 
from pandas import DataFrame
from cost_functions import *

import tensorflow as tf


class Context:
    def __init__(self,account):
        self.account = account

class TradeEngine:
    
    trades = []
    cost_functions = costs
    history_status = []

    def __init__(self,strategy,historybins,initialCurrency,trade_cost=0.00025,cost_functions_list=[]):
        '''
            startegy: 策略对象实例。
            historybins: tf.Tensor的一个实例，它的形状为(bin中时间序列总长度）
            cost_function_list
        '''
        self.account = Account(initialCurrency,trade_cost)
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
                if current_bin.end_date >= trade.expire_date:
                    self.account.trade_failed(trade)
                    self.strategy.handle_trade(trade,0)
                else:
                    new_trades.append(trade)
                    self.strategy.handle_trade(trade,-1)
        
        return new_trades

    def run_backtest(self):


        print('backtest start')

        bin_length = len(self.historybins)

        for i in range(bin_length-1):
            current_bin = self.historybins[i]
            next_bin = self.historybins[i+1]
            
            requests = self.strategy.make_trade(current_bin,self.ctx)

            self.validate_requested_trades(requests)

            self.trades = self.handle_requested_trades(current_bin,next_bin)

            self.save_status(current_bin.end_date)

            if i % 1000 == 0 :
                print(f'{i} bin done. {current_bin.end_date}')


        return self.calculate_cost()

    def save_status(self,date):
        self.history_status.append({
          "date":date,
          "currency":self.account.currency+self.account.frozen,
          "amounts":self.account.amounts
        })
    
    def calculate_cost(self):

        bins = self.historybins
        
        # 我们用后一段时间的数据来和这个时刻的状态做对应

        print('Converting The Result into DataFrame.')

        converted_status = DataFrame(data=[{
            "ask_low":bins[i+1].ask_low,
            "ask_high":bins[i+1].ask_high,
            "ask_open":bins[i+1].ask_open,
            "ask_close":bins[i+1].ask_close,
            "bid_low":bins[i+1].bid_low,
            "bid_high":bins[i+1].bid_high,
            "bid_open":bins[i+1].bid_open,
            "bid_close":bins[i+1].bid_close ,
            "currency":self.history_status[i]["currency"],
            "amounts":self.history_status[i]["amounts"]
        } for i in range(len(self.historybins)-1)] )

        print('Converting accomplish,start to calculate costs')

        result_lists = [cost(history_status=converted_status) for cost in self.cost_functions]

        return result_lists