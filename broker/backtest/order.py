import order


class BackTestingOrder:
    # Override to call the fill strategy using the concrete order type.
    # return FillInfo or None if the order should not be filled.
    def process(self, broker_, bar_):
        raise NotImplementedError()


class MarketOrder(order.MarketOrder, BackTestingOrder):
    def __init__(self, action, instrument, quantity, on_close, instrument_traits):
        super(MarketOrder, self).__init__(action, instrument, quantity, on_close, instrument_traits)

    def process(self, broker_, bar_):
        return broker_.getFillStrategy().fillMarketOrder(broker_, self, bar_)


class LimitOrder(order.LimitOrder, BackTestingOrder):
    def __init__(self, action, instrument, price, quantity, instrument_traits):
        super(LimitOrder, self).__init__(action, instrument, price, quantity, instrument_traits)

    def process(self, broker_, bar_):
        return broker_.getFillStrategy().fillLimitOrder(broker_, self, bar_)


class StopOrder(order.StopOrder, BackTestingOrder):
    def __init__(self, action, instrument, price, quantity, instrument_traits):
        super(StopOrder, self).__init__(action, instrument, price, quantity, instrument_traits)
        self.__stopHit = False

    def process(self, broker_, bar_):
        return broker_.getFillStrategy().fillStopOrder(broker_, self, bar_)

    @property
    def stop_hit(self):
        return self.__stopHit

    @stop_hit.setter
    def stop_hit(self, value):
        self.__stopHit = value


# http://www.sec.gov/answers/stoplim.htm
# http://www.interactivebrokers.com/en/trading/orders/stopLimit.php
class StopLimitOrder(order.StopLimitOrder, BackTestingOrder):
    def __init__(self, action, instrument, stop_price, limit_price, quantity, instrument_traits):
        super(StopLimitOrder, self).__init__(action, instrument, stop_price, limit_price, quantity, instrument_traits)
        self.__stopHit = False  # Set to true when the limit order is activated (stop price is hit)

    @property
    def stop_hit(self):
        return self.__stopHit

    @stop_hit.setter
    def stop_hit(self, value):
        self.__stopHit = value

    def process(self, broker_, bar_):
        return broker_.getFillStrategy().fillStopLimitOrder(broker_, self, bar_)
