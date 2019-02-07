from datetime import datetime
from order.commission import Commission
from order.order import Order


class Execution:
    def __init__(self, price: float, quantity: float, commission: Commission, dateTime: datetime):
        self.__price = price
        self.__quantity = quantity
        self.__commission = commission
        self.__dateTime = dateTime

    def __str__(self):
        return "%s - Price: %s - Amount: %s - Fee: %s" % (
            self.__dateTime, self.__price, self.__quantity, self.__commission)

    @property
    def price(self):
        """Returns the fill price."""
        return self.__price

    @property
    def quantity(self):
        """Returns the quantity."""
        return self.__quantity

    @property
    def total(self):
        return self.__quantity * self.__price

    @property
    def commission(self):
        """Returns the commission applied."""
        return self.__commission

    def calculate_commission(self, order: Order):
        return self.commission.calculate(order, self.price, self.quantity)

    @property
    def datetime(self):
        """Returns the :class:`datetime.datetime` when the order was executed."""
        return self.__dateTime
