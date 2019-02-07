
class Account:
    '''
        存储了用户所持有种类和商品的数量等等
    '''
    def __init__(self,currency,trade_cost):
        self.amounts = 0.0
        self.currency = currency
        self.trade_cost = trade_cost
        self.frozen_cur = 0.0
        self.frozen_amo = 0.0
        self.start_cur = currency

    def assets(self,price):
        return self.currency + self.amounts * (1-self.trade_cost) * price
    def max_in(self,price):
        return self.avaliable_cur() / ((1+self.trade_cost)*price)
        
    def max_out(self):
        return self.avaliable_amo()

    def avaliable_cur(self):
        return self.currency-self.frozen_cur
    def avaliable_amo(self):
        return self.amounts-self.frozen_amo


    def to_trust_trade(self,trade):
        can_trust = self.trade_avaliable(trade)

        if can_trust:
            self.trade_trust(trade)

        return can_trust
    def trade_avaliable(self,trade):
        '''
            判断账上的资金是否足以挂单，即这个单子是否本身是有效的
        '''
        if(trade.type == 'limit'):

            total = trade.price * trade.amounts

            if trade.des == 'in':
                return self.avaliable_cur() >= total * (1+self.trade_cost)
            elif trade.des == 'out':
                return self.avaliable_amo() >= trade.amounts 
            else:
                return False
        else:
            return False

    def trade_trust(self,trade):
        price = trade.price
        des = trade.des
        amounts = trade.amounts
        if(trade.type == 'limit'):

            total = price * amounts

            if(des == 'in'):
                self.frozen_cur += total * (1+self.trade_cost)
            elif(des == 'out'):
                self.frozen_amo += trade.amounts

        elif(trade.type == 'market'):
            '''
                市价委托暂时没有实现
            '''
            pass

    def trade_success(self,trade):
        price = trade.price
        des = trade.des
        amounts = trade.amounts

        total = price * amounts
        cost = total * self.trade_cost
        
        if(trade.type == 'limit'):
            if(des == 'in'):
                self.amounts+=amounts
                self.frozen_cur -= cost + total
                self.currency -= cost + total

                if(self.frozen_cur <=1e-3):
                    self.frozen_cur = 0
                if(self.currency <= 1e-3):
                    self.currency =0

            elif(des == 'out'):
                self.currency+=price*amounts-cost
                self.frozen_amo -= amounts
                self.amounts -= amounts

                if(self.frozen_amo <=1e-3):
                    self.frozen_amo = 0
                if(self.amounts <= 1e-3):
                    self.amounts =0
        elif(trade.type == 'market'):
            '''
                市价委托暂时没有实现
            '''
            pass
    def trade_failed(self,trade):
        price = trade.price
        des = trade.des
        amounts = trade.amounts

        total = price * amounts
        cost = total * self.trade_cost

        if(trade.type == 'limit'):
            if(des == 'in'):
                self.frozen_cur -= cost + total

                if(self.frozen_cur <= 1e-3):
                    self.frozen_cur = 0
            elif(des == 'out'):
                self.frozen_amo -= amounts

                if(self.frozen_amo <= 1e-3):
                    self.frozen_amo =0

        elif(trade.type == 'market'):
            '''
                市价委托暂时没有实现
            '''
            pass

    def __repr__(self):
        return 'amounts:%.3f forzen_amounts:%.3f cur:%.3f frozen:%.3f' %(self.amounts,self.frozen_amo,self.currency,self.frozen_cur,)