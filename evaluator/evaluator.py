from cost_functions import costs

class Evaluator:
    def __init__(self,history_status,trade_cost=0.00025):
        self.history_status = history_status
        self.trade_cost = trade_cost
        self.result_lists = {}
        self.ctx ={
            "trade_cost":trade_cost
        }
    
    def calculate_cost(self):

        self.result_lists = {}

        for k,v in costs.items():
            self.result_lists[k] = v(self.history_status,self.result_lists,self.ctx)

        return self.result_lists

    