import datetime
from engine.account import Account
class Trade:
    def __init__(self,type,des,trust_date:datetime.datetime,amounts=0.0,price=0.0,expire_delta:datetime.timedelta=None,account:Account=None):
        '''
            type 表示交易委托的种类
                limit 限价委托
                market 市价委托
            amount 交易数量
            price 交易价格
            des 标的 0买1卖
        '''
        self.type=type
        self.des = des
        self.amounts= amounts
        self.price = price
        self.account = account
        self.expire_delta = expire_delta
        self.status = 'pending'
        self.made_date = None
        self.trust_date = trust_date


    def to_trust(self):
        return self.account.to_trust_trade(self)

    def to_made(self,current_bin,next_bin):
        '''
            计算是否达到成交条件，或者是否已经到期
            如果满足条件，返回True,
            不然，返回False（还未达到条件，并且还挂着）
        '''

        success = False

        if(self.type == 'limit'):
            if self.des == 'in':
                success = self.price >= current_bin.ask_low \
                    and self.price < next_bin.ask_close 
            elif self.des == 'out':
                success = self.price <= current_bin.bid_high \
                    and self.price > next_bin.bid_close
                    # 卖出的时候，要求被卖的数量要多一些


        # Not Implemented
        elif self.type == 'market':
            success = True
        else:
            success =  False

        return (self.made if success else self.check_expired)(next_bin.end_date)

    def made(self,date):
        self.made_date = date
        self.status = 'success'
        self.account.trade_success(self)
        return True

    def check_expired(self,date):
        '''
            给出当前时间，检查交易是否已经到期
            如果已经到期，瞬间判定为交易失败
            返回是否到期
        '''
        if(self.trust_date + self.expire_delta >=date):
            self.status = 'failed'
            self.made_date = date
            self.account.trade_failed(self)
            return True
        else:
            return False
    def __repr__(self):
        return '[%s at %s-type:%s-des:%s]\tamounts:%.3f price:%.3f trust:%s expire:%s ' %\
            (self.status,self.made_date,self.type,self.des,self.amounts,self.price,self.trust_date,self.expire_delta)


