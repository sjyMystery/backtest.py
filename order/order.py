from order.action import Action
from order.state import State
from order.type import Type
from order.execution import Execution

from datetime import datetime

import functools


class Order:
    def __init__(self, type_: Type, action: Action, instrument, quantity: float, instrument_traits):
        assert quantity is not None and quantity > 0
        assert type_ in Type

        self.__state = State.INITIAL
        self.__type = type_
        self.__action = action
        self.__quantity = quantity
        self.__executionInfo = []
        self.__instrument = instrument
        self.__instrument_traits = instrument_traits
        self.__good_till_canceled = False
        self.__allOrNone = False
        self.__id = None
        self.__submitted_at = None
        self.__canceled_at = None
        self.__accepted_at = None

    @property
    def good_till_canceled(self):
        return self.__good_till_canceled

    @good_till_canceled.setter
    def good_till_canceled(self, value):
        assert self.__state == State.INITIAL
        self.__good_till_canceled = value

    @property
    def all_or_one(self):
        return self.__allOrNone

    @all_or_one.setter
    def all_or_one(self, value):
        assert self.__state == State.INITIAL
        self.__allOrNone = value

    @property
    def type(self):
        return self.__type

    @property
    def is_buy(self):
        return self.action in [Action.BUY, Action.BUY_TO_COVER]

    @property
    def is_sell(self):
        return self.action in [Action.SELL, Action.SELL_SHORT]

    @property
    def is_active(self):
        return self.state not in [State.CANCELED, State.FILLED]

    @property
    def action(self):
        return self.__action

    @property
    def instrument(self):
        return self.__instrument

    @property
    def quantity(self):
        return self.__quantity

    def append_execution(self, execution: Execution):
        self.__executionInfo.append(execution)

    @property
    def executions(self):
        return self.__executionInfo

    @property
    def filled(self):
        def sum_quantity(x, y):
            return x + y.quantity

        return functools.reduce(sum_quantity, self.executions, 0)

    @property
    def filled_cost(self):
        def sum_total(x, y):
            return x + y.total

        return functools.reduce(sum_total, self.executions, 0)

    @property
    def total_commission(self):
        def sum_total(x, y: Execution):
            return x + y.commission.calculate(self, y.price)

        return functools.reduce(sum_total, self.executions, 0)

    @property
    def avg_fill_price(self):
        return self.filled_cost / float(self.filled)

    @property
    def remain(self):
        return self.__instrument_traits.roundQuantity(self.quantity - self.filled)

    def submitted(self, _id, at: datetime):
        self.__id = _id
        self.__submitted_at = at
        return self

    def canceled(self, at: datetime):
        self.__canceled_at = at
        return self

    def accepted(self, at: datetime):
        self.__accepted_at = at
        return self

    @property
    def submitted_at(self):
        return self.__submitted_at

    @property
    def canceled_at(self):
        return self.__canceled_at

    @property
    def accepted_at(self):
        return self.__accepted_at

    @property
    def state(self):
        if self.canceled_at is not None:
            return State.CANCELED
        if self.submitted_at is None:
            return State.INITIAL

        if self.accepted_at is None:
            return State.SUBMITTED

        if self.filled is 0:
            return State.ACCEPTED
        elif self.remain is 0:
            return State.FILLED
        else:
            return State.PARTIALLY_FILLED

    @property
    def is_canceled(self):
        return self.state == State.CANCELED

    @property
    def is_submitted(self):
        return self.state == State.SUBMITTED

    @property
    def is_accepted(self):
        return self.state == State.ACCEPTED

    @property
    def is_filled(self):
        return self.state == State.FILLED

    @property
    def is_partially_filled(self):
        return self.state == State.PARTIALLY_FILLED

    @property
    def is_initial(self):
        return self.state == State.INITIAL
