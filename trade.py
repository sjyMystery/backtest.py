

class Trade:
    def __init__(self,type,des,amount=None,price=None):
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
        self.amount= amount
        self.price = price
        pass