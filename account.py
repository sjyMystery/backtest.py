
class Account:
    '''
        存储了用户所持有种类和商品的数量等等
    '''
    def __init__(self,currency):
        self.amounts = 0.0
        self.currency = currency

    def trade_avaliable(self,trade):
        '''
            判断账上的资金是否足以挂单，即这个单子是否本身是有效的
        '''
        if(trade.type == 'limit'):
            if trade.des == 'in':
                return self.currency >= trade.price*trade.amount
            elif trade.des == 'out':
                return self.amounts >= trade.amount
            else:
                return False
        else:
            return False

    def trade_trust(self,trade):
        price = trade.price
        des = trade.des
        amount = trade.amount
        if(trade.type == 'limit'):
            if(des == 'in'):
                self.currency-=price*amount
            elif(des == 'out'):
                self.currency+=price*amount
        elif(trade.type == 'market'):
            '''
                市价委托暂时没有实现
            '''
            pass
    def trade_success(self,trade):
        price = trade.price
        des = trade.des
        amount = trade.amount
        
        if(trade.type == 'limit'):
            if(des == 'in'):
                self.amounts+=amount
            elif(des == 'out'):
                self.currency+=price*amount
        elif(trade.type == 'market'):
            '''
                市价委托暂时没有实现
            '''
            pass
    def trade_failed(self,trade):
        price = trade.price
        des = trade.des
        amount = trade.amount
        if(trade.type == 'limit'):
            if(des == 'in'):
                self.currency+=price*amount
            elif(des == 'out'):
                self.currency-=price*amount
        elif(trade.type == 'market'):
            '''
                市价委托暂时没有实现
            '''
            pass
