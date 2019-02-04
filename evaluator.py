from cost_functions import costs

class Evaluator:
    def __init__(self,history_status,trade_cost):
        self.history_status = history_status
        self.trade_cost = trade_cost

        self.ctx ={
            "trade_cost":trade_cost
        }
    
    def calculate_cost(self):

        result_lists = {}

        for k,v in costs.items():
            result_lists[k] = v(self.history_status,result_lists,self.ctx)

        return result_lists