from order.action import Action
from order.state import State
from order.type import Type
from order.execution import Execution

from datetime import datetime

import functools

class Order:


    VALID_TRANSITIONS = {
        State.INITIAL : [State.SUBMITTED,State.CANCELLED],
        State.SUBMITTED : [State.ACCEPTED,State.CANCELLED],
        State.ACCEPTED : [State.PARTIALLY_FILLED,State.FILLED,State.CANCELLED],
        State.PARTIALLY_FILLED : [State.PARTIALLY_FILLED,State.FILLED,State.CANCELLED]
    }

    def __init__(self,type_:Type,action:Action,instrument,quantity,instrumentTraits):
        assert quantity is not None and quantity > 0
        assert type_ in Type

        self.__state = State.INITIAL
        self.__type = type_
        self.__action = action
        self.__quantity = quantity
        self.__executionInfo = []
        self.__instrument = instrument
        self.__goodTillCanceled = False
        self.__allOrNone =False

        self.__submitted_at = None
        self.__cancelled_at = None
        self.__accepted_at = None

    @property
    def type(self):
        return self.__type
    @property
    def is_buy(self):
        return self.action in [Action.BUY,Action.BUY_TO_COVER]
    @property
    def is_sell(self):
        return self.action in [Action.SELL,Action.SELL_SHORT]
    @property
    def is_active(self):
        return self.state not in [Order.State.CANCELED, Order.State.FILLED]
    @property
    def action(self):
        return self.__action
    @property
    def instruument(self):
        return self.__instrument
    @property
    def quantity(self):
        return self.__quantity

    @property
    def quantity(self):
        return self.__quantity

    def append_execution(self,execution:Execution):
        self.__executionInfo .append(execution)
        
    @property
    def executions(self):
        return self.__executionInfo

    @property
    def filled(self):
        def sum_quantity(x,y):
            return x+y.quantity
        return functools.reduce(sum_quantity,self.executions,0)
    
    @property
    def filled_cost(self):
        def sum_total(x,y):
            return x+y.total
        return functools.reduce(sum_total,self.executions,0)
    
    @property
    def total_commission(self):
        def sum_total(x,y:Execution):
            return x+y.commission.calculate(self,y.price,y.)
        return functools.reduce(sum_total,self.executions,0)
    

    @property
    def avg_fill_price(self):
        return self.filled_cost/float(self.filled)
    
    @property
    def remain(self):
        return self.__instrumentTraits.roundQuantity(self.quantity-self.filled)

    def submitted(self,orderId,dateTime:datetime):
        self.__id = orderId
        self.__submitted_at = dateTime
        return self
    def cancelled(self,at:datetime):
        self.cancelled_at = at
        return self
    def accepted(self,at:datetime):
        self.__accepted_at = at
        return self

    @property
    def submitted_at(self):
        return self.__submitted_at

    @property
    def cancelled_at(self):
        return self.__cancelled_at

    @property
    def accepted_at(self):
        return self.__accepted_at

    @property
    def state(self):
        if self.cancelled_at is not None:
            return State.CANCELLED 
        if self.submitted_at is None:
            return State.INITIAL

        if self.accepted_at is None:
            return State.SUBMITTED
        
        if self.filled is 0 :
            return State.ACCEPTED
        elif self.remain is 0 :
            return State.FILLED
        else:
            return State.PARTIALLY_FILLED