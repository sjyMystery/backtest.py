import tensorflow as tf
from tensorflow.contrib import autograph


class Account:
    '''
        存储了用户所持有种类和商品的数量等等
    '''
    def __init__(self,currency):
        self.amounts = tf.Variable(0,dtype=tf.float32)
        self.currency = tf.Variable(currency,dtype=tf.float32)

    @autograph.convert()
    def trade(self,trade):
        price = trade.price
        des = trade.des
        amount = trade.amount
        
        if(trade.type == 'limit'):
            if(des == 'in'):
                self.currency-=price*amount
                self.amounts+=amount
            elif(des == 'to'):
                self.currency+=price*amount
                self.amounts-=amount
        elif(trade.type == 'market'):
            '''
                市价委托暂时没有实现
            '''
            pass
        
class Context:
    def __init__(self,account,instruments):
        self.account = account
        self.instruments = instruments

class RunGraphBuilder:
    def __init__(self,strategy,historybins,initialCurrency):
        '''
            startegy: 策略对象实例。
            historybins: tf.Tensor的一个实例，它的形状为(bin中时间序列总长度)
        '''
        self.account = Account(initialCurrency)
        self.ctx = Context(self.account)
        self.strategy = strategy
        self.historybins = historybins


    @autograph.convert()
    def judge_trade(self,trade,current_bin,next_bin):
        '''
            计算是否达到成交条件
        '''
        if(trade.type == 'limit'):
            if trade.des == 'in':
                return trade.price >= current_bin.ask_low \
                    and trade.price < next_bin.ask_close \
                    and self.account.currency >= trade.price*trade.amount
            elif trade.des == 'out':
                return trade.price <= current_bin.bid_heigh \
                    and trade.price > next_bin.bid_close \
                    and self.account.amounts >= trade.amount
                    # 卖出的时候，要求被卖的数量要多一些
        elif trade.type == 'market':
            return True
        else :
            return False

    @autograph.convert()
    def run_bin(self,current_bin,next_bin):
        '''
            对于每一个时刻进行计算，得到下一时刻的数据

            current_bins和next_bins均为以instrument.name为键的一个字典
        '''

        trades = self.strategy.make_trade(current_bin,self.ctx)


        bin_ops = []


        for trade in trades:
            tradable = self.judge_trade(trade,current_bin,next_bin)
            if(tradable):
                bin_ops.append(self.account.trade(trade))
                bin_ops.append(self.strategy.handle_result(True,self.ctx))
            else:
                 bin_ops.append(self.strategy.handle_result(False,self.ctx))
        return bin_ops


    @autograph.convert()
    def make_backtest_graph(self,all_bins):
        length = len(all_bins)
        bin_ops = []
        autograph.set_element_type(bin_ops,tf.placeholder)
        for i in range(length):
            if i==length-2:
                break
            bin_ops += self.run_bin(all_bins[i],all_bins[i+1])

        return autograph.stack(bin_ops)

