
class Account:
    '''
        存储了用户所持有种类和商品的数量等等
    '''
    def __init__(self,currency,trade_cost):
        self.amounts = 0.0
        self.currency = currency
        self.trade_cost = trade_cost
        self.frozen = 0.0

    def trade_avaliable(self,trade):
        '''
            判断账上的资金是否足以挂单，即这个单子是否本身是有效的
        '''
        if(trade.type == 'limit'):

            total = trade.price * trade.amounts

            if trade.des == 'in':
                return self.currency >= total * (1+self.trade_cost)
            elif trade.des == 'out':
                return self.amounts >= trade.amounts and self.currency >= self.trade_cost * total
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
                self.currency-= total * (1+self.trade_cost)
                self.frozen += total * self.trade_cost
            elif(des == 'out'):
                self.currency+=total
                self.frozen += total * self.trade_cost

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
                self.frozen -= cost
            elif(des == 'out'):
                self.currency+=price*amounts
                self.frozen -= cost
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
                
                self.currency+= (price*amounts+cost)
                self.frozen -= cost

            elif(des == 'out'):
                
                self.currency-=(price*amounts-cost)
                self.frozen -= cost

        elif(trade.type == 'market'):
            '''
                市价委托暂时没有实现
            '''
            pass
