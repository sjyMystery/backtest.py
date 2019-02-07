from cost_functions import costs
from pandas import DataFrame,pandas
from engine.engine import Context
from matplotlib.pyplot import show
class Evaluator:
    def __init__(self,history_status:DataFrame,ctx:Context,trades_csv="trades.csv",histories_csv='histories.csv'):
        self.history_status = history_status
        self.result_lists = {}
        self.ctx=ctx


        history_trades = self.ctx.made_trades

        trade_list = []
        index = []

        for trade in history_trades:
            dic = trade.to_dict()
            trade_list.append(dic)
            index.append(dic["made_date"])

        self.trades=DataFrame(trade_list,index=index)
        if(histories_csv):
            self.history_status.to_csv(histories_csv)
        if(trades_csv):
            self.trades.to_csv(trades_csv)
    def calculate_cost(self):

        self.result_lists = {}

        for k,v in costs.items():
            self.result_lists[k] = v(self.history_status,self.result_lists,self.ctx)

        return self.result_lists



    def run(self):
        print(self.calculate_cost())
        for trade in self.trades:
            print(trade)
        self.show_images()
    def show_images(self):


    
        candle_data = self.history_status[['ask_close','bid_close']]
        line1 = candle_data.plot.line(title='price')
        assets = self.history_status[['assets','currency','frozen_currency']]
        line2 = assets.plot.line(title='assets')
        amounts = self.history_status[['amounts','frozen_amounts']]
        line3 = amounts.plot.line(title='amounts')
        show()