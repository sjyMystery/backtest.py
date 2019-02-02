'''
    basic_stategy.py
    ----------------
    This file gives out a outline of a strategy, all strategy must be children of this class.
'''

class BasicStratgy:
    def __init__(self):
        pass

    def make_trade(self,bins,ctx):
        '''
            bins: 当前时刻的所有交易信息
            ctx: 交易的上下文信息（包含过去的一些信息）
            returns: 期望执行的交易列表，应该是一个Trade对象的列表。
        '''
        pass
    def handle_result(self,result,ctx):
        '''
            result: 交易的结果，按照make_decicsion返回的顺序返回.
            ctx: 执行交易后的上下文情况
        '''
        pass

