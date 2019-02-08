import broker
import logger
import six
import bar
from bar import Bar, Bars
from order import Commission, NoCommission, IntegerTraits, InstrumentTraits, Execution, OrderEvent, Order, Action
from broker.backtest.order import BackTestingOrder, LimitOrder, StopOrder, MarketOrder, StopLimitOrder
from broker.backtest.fillstrategy import FillInfo, DefaultStrategy
import order
from datetime import datetime


class Broker(broker.Broker):
    """BackTesting broker.

    :param cash: The initial amount of cash.
    :type cash: int/float.
    :param barFeed: The bar feed that will provide the bars.
    :type barFeed: :class:`pyalgotrade.barfeed.BarFeed`
    :param commission: An object responsible for calculating order commissions.
    :type commission: :class:`Commission`
    """

    LOGGER_NAME = "broker.backtesting"

    def __init__(self, cash, bar_feed, commission: Commission = None):
        super(Broker, self).__init__(cash, bar_feed=bar_feed, commission=commission)

        assert (cash >= 0)
        self.__cash = cash
        if commission is None:
            self.__commission = NoCommission()
        else:
            self.__commission = commission
        self.__shares = {}
        self.__instrumentPrice = {}  # Used by setShares
        self.__activeOrders = {}
        self.__useAdjustedValues = False
        self.__fillStrategy = DefaultStrategy()
        self.__logger = logger.get_logger(Broker.LOGGER_NAME)

        # It is VERY important that the broker subscribes to barfeed events before the strategy.
        bar_feed.getNewValuesEvent().subscribe(self.on_bars)

        self.__barFeed = bar_feed
        self.__nextOrderId = 1
        self.__started = False

    @property
    def next_order_id(self):
        ret = self.__nextOrderId
        self.__nextOrderId += 1
        return ret

    def get_bar(self, bars, instrument):
        ret = bars.getBar(instrument)
        if ret is None:
            ret = self.__barFeed.getLastBar(instrument)
        return ret

    def register_order(self, order_: Order):
        assert (order_.id not in self.__activeOrders)
        assert (order_.id is not None)
        self.__activeOrders[order_.id] = order

    def unregister_order(self, order_: Order):
        assert (order_.id in self.__activeOrders)
        assert (order_.id is not None)
        del self.__activeOrders[order_.id]

    @property
    def logger(self):
        return self.__logger

    def cash(self, include_short=True):
        ret = self.__cash
        if not include_short and self.__barFeed.getCurrentBars() is not None:
            bars = self.__barFeed.getCurrentBars()
            for instrument, shares in six.iteritems(self.__shares):
                if shares < 0:
                    instrument_price = self._getBar(bars, instrument).price
                    ret += instrument_price * shares
        return ret

    @property
    def commission(self):
        """Returns the strategy used to calculate order commissions.

        :rtype: :class:`Commission`.
        """
        return self.__commission

    @commission.setter
    def commission(self, commission):
        """Sets the strategy to use to calculate order commissions.

        :param commission: An object responsible for calculating order commissions.
        :type commission: :class:`Commission`.
        """

        self.__commission = commission

    @property
    def fill_strategy(self):
        return self.__fillStrategy

    @fill_strategy.setter
    def fill_strategy(self, strategy):
        self.__fillStrategy = strategy

    @property
    def use_adjusted_values(self):
        return self.__useAdjustedValues

    @use_adjusted_values.setter
    def use_adjusted_values(self, use_adjusted):
        # Deprecated since v0.15
        if not self.__barFeed.barsHaveAdjClose():
            raise Exception("The barfeed doesn't support adjusted close values")
        self.__useAdjustedValues = use_adjusted

    def active_orders(self, instrument=None):
        if instrument is None:
            ret = list(self.__activeOrders.values())
        else:
            ret = [order_ for order_ in self.__activeOrders.values() if order_.instrument == instrument]
        return ret

    @property
    def current_datetime(self):
        return self.__barFeed.current_datetime

    def instrument_traits(self, instrument):
        return IntegerTraits()

    def get_shares(self, instrument):
        return self.__shares.get(instrument, 0)

    def set_shares(self, instrument, quantity, price):
        """
        Set existing shares before the strategy starts executing.

        :param instrument: Instrument identifier.
        :param quantity: The number of shares for the given instrument.
        :param price: The price for each share.
        """

        assert not self.__started, "Can't setShares once the strategy started executing"
        self.__shares[instrument] = quantity
        self.__instrumentPrice[instrument] = price

    @property
    def positions(self):
        return self.__shares

    @property
    def active_instruments(self):
        return [instrument for instrument, shares in six.iteritems(self.__shares) if shares != 0]

    def _get_price_for_instrument(self, instrument):
        ret = None

        # Try gettting the price from the last bar first.
        last_bar = self.__barFeed.getLastBar(instrument)
        if last_bar is not None:
            ret = last_bar.price
        else:
            # Try using the instrument price set by setShares if its available.
            ret = self.__instrumentPrice.get(instrument)

        return ret

    @property
    def equity(self):
        """Returns the portfolio value (cash + shares * price)."""

        ret = self.cash()
        for instrument, shares in six.iteritems(self.__shares):
            instrument_price = self._get_price_for_instrument(instrument)
            assert instrument_price is not None, "Price for %s is missing" % instrument
            ret += instrument_price * shares
        return ret

    # Tries to commit an order execution.
    def commit_order_execution(self, order_: Order, datetime_: datetime, fill_info: FillInfo):
        price = fill_info.price
        quantity = fill_info.quantity

        if order_.is_buy:
            cost = price * quantity * -1
            assert (cost < 0)
            shares_delta = quantity
        elif order_.is_sell:
            cost = price * quantity
            assert (cost > 0)
            shares_delta = quantity * -1
        else:  # Unknown action
            assert False

        commission = self.commission.calculate(order_, price, quantity)
        cost -= commission
        resulting_cash = self.cash() + cost

        # Check that we're ok on cash after the commission.
        if resulting_cash >= 0:

            # Update the order before updating internal state since addExecutionInfo may raise.
            # addExecutionInfo should switch the order state.
            execution = Execution(price, quantity, commission, datetime_)
            order_.append_execution(execution)

            # Commit the order execution.
            self.__cash = resulting_cash

            updated_shares = order_.instrument_traits.roundQuantity(
                self.getShares(order_.instrument) + shares_delta
            )
            if updated_shares == 0:
                del self.__shares[order_.instrument]
            else:
                self.__shares[order_.instrument] = updated_shares

            # Let the strategy know that the order was filled.
            self.__fillStrategy.on_order_filled(self, order_)

            # Notify the order update
            if order_.is_filled:
                self.unregister_order(order_)
                self.notify_order_event(order.OrderEvent(order_, order.State.FILLED, execution))
            elif order_.is_partially_filled:
                self.notify_order_event(order.OrderEvent(order_, order.State.PARTIALLY_FILLED, execution))
            else:
                assert False
        else:
            self.__logger.debug("Not enough cash to fill %s order [%s] for %s share/s" % (
                order_.instrument,
                order_.id,
                order_.remain
            ))

    def submit_order(self, order_: Order):
        if order_.is_initial:
            order_.submitted(self.next_order_id, self.current_datetime)
            self.register_order(order_)
            self.notify_order_event(order.OrderEvent(order_, order.State.SUBMITTED, None))
        else:
            raise Exception("The order was already processed")

    # Return True if further processing is needed.
    def __preprocess_order(self, order_: Order, bar_):
        ret = True

        # For non-GTC orders we need to check if the order has expired.
        if not order_.good_till_canceled:

            current = bar_.datetime

            expired = current.date() > order_.accepted_at.date()

            # Cancel the order if it is expired.
            if expired:
                ret = False
                self.unregister_order(order_)
                order_.canceled(current)
                self.notify_order_event(order.OrderEvent(order_, order.Type.CANCELED, "Expired"))

        return ret

    def __postprocess_order(self, order_: Order, bar_: bar.Bar):
        # For non-GTC orders and daily (or greater) bars we need to check if orders should expire right now
        # before waiting for the next bar.
        if not order_.good_till_canceled:
            expired = False
            if self.__barFeed.getFrequency() >= bar.Frequency.DAY:
                expired = bar_.datetime.date() >= order_.accepted_at.date()

            # Cancel the order if it will expire in the next bar.
            if expired:
                self.unregister_order(order_)
                order_.canceled(bar_.datetime)
                self.notify_order_event(broker.OrderEvent(order_, order.State.CANCELLED, "Expired"))

    def __process_order(self, order_, bar_: Bar):
        if not self.__preprocess_order(order_, bar_):
            return
        # Double dispatch to the fill strategy using the concrete order type.
        fill_info = order_.process(self, bar_)
        if fill_info is not None:
            self.commit_order_execution(order_, bar_.datetime, fill_info)

        if order_.is_active:
            self.__postprocess_order(order_, bar_)

    def __on_bars_impl(self, order_, bars: Bars):
        # IF WE'RE DEALING WITH MULTIPLE INSTRUMENTS WE SKIP ORDER PROCESSING IF THERE IS NO BAR FOR THE ORDER'S
        # INSTRUMENT TO GET THE SAME BEHAVIOUR AS IF WERE BE PROCESSING ONLY ONE INSTRUMENT.
        bar_ = bars.bar(order_.instrument)
        if bar_ is not None:
            # Switch from SUBMITTED -> ACCEPTED
            if order_.is_submitted:
                order_.accepted(bar_.datetime)
                self.notify_order_event(broker.OrderEvent(order_, order.State.ACCEPTED, None))

            if order_.is_active:
                # This may trigger orders to be added/removed from __activeOrders.
                self.__process_order(order_, bar_)
            else:
                # If an order is not active it should be because it was canceled in this same loop and it should
                # have been removed.
                assert order_.is_canceled
                assert order_ not in self.__activeOrders

    def on_bars(self, datetime_, bars):
        # Let the fill strategy know that new bars are being processed.
        self.__fillStrategy.on_bars(self, bars)

        # This is to froze the orders that will be processed in this event, to avoid new getting orders introduced
        # and processed on this very same event.
        orders_to_process = list(self.__activeOrders.values())

        for order_ in orders_to_process:
            # This may trigger orders to be added/removed from __activeOrders.
            self.__on_bars_impl(order_, bars)

    def start(self):
        super(Broker, self).start()
        self.__started = True

    def stop(self):
        pass

    def join(self):
        pass

    def eof(self):
        # If there are no more events in the barfeed, then there is nothing left for us to do since all processing took
        # place while processing barfeed events.
        return self.__barFeed.eof()

    def dispatch(self):
        # All events were already emitted while handling barfeed events.
        pass

    def peek_datetime(self):
        return None

    def create_market_order(self, action: Action, instrument: str, quantity: float, on_close=False):
        # In order to properly support market-on-close with intraday feeds I'd need to know about different
        # exchange/market trading hours and support specifying routing an order to a specific exchange/market.
        # Even if I had all this in place it would be a problem while paper-trading with a live feed since
        # I can't tell if the next bar will be the last bar of the market session or not.
        if on_close is True and self.__barFeed.isIntraday():
            raise Exception("Market-on-close not supported with intraday feeds")

        return MarketOrder(action, instrument, quantity, on_close, self.instrument_traits(instrument))

    def create_limit_order(self, action: Action, instrument: str, price: float, quantity: float):
        return LimitOrder(action, instrument, price, quantity, self.instrument_traits(instrument))

    def create_stop_order(self, action: Action, instrument: str, price: float, quantity: float):
        return StopOrder(action, instrument, price, quantity, self.instrument_traits(instrument))

    def create_stop_limit_order(self, action: Action, instrument: str, stop_price: float, limit_price: float,
                                quantity: float):
        return StopLimitOrder(action, instrument, stop_price, limit_price, quantity, self.instrument_traits(instrument))

    def cancel_order(self, order_: Order):
        active_order = self.__activeOrders.get(order_.id)
        if active_order is None:
            raise Exception("The order is not active anymore")
        if active_order.isFilled():
            raise Exception("Can't cancel order that has already been filled")

        self.unregister_order(active_order)
        active_order.switchState(order.State.CANCELED)
        self.notify_order_event(
            broker.OrderEvent(active_order, order.State.CANCELED, "User requested cancellation")
        )
