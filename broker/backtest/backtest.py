import broker
import logger
import six
from order import Commission,NoCommission


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
        super(Broker, self).__init__()

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
        self.__fillStrategy = fillstrategy.DefaultStrategy()
        self.__logger = logger.get_logger(Broker.LOGGER_NAME)

        # It is VERY important that the broker subscribes to barfeed events before the strategy.
        bar_feed.getNewValuesEvent().subscribe(self.onBars)

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

    def register_order(self, order):
        assert (order.getId() not in self.__activeOrders)
        assert (order.getId() is not None)
        self.__activeOrders[order.getId()] = order

    def unregister_order(self, order):
        assert (order.getId() in self.__activeOrders)
        assert (order.getId() is not None)
        del self.__activeOrders[order.getId()]

    @property
    def logger(self):
        return self.__logger

    def get_cash(self, include_short=True):
        ret = self.__cash
        if not include_short and self.__barFeed.getCurrentBars() is not None:
            bars = self.__barFeed.getCurrentBars()
            for instrument, shares in six.iteritems(self.__shares):
                if shares < 0:
                    instrument_price = self._getBar(bars, instrument).getPrice()
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


    def setFillStrategy(self, strategy):
        """Sets the :class:`pyalgotrade.broker.fillstrategy.FillStrategy` to use."""
        self.__fillStrategy = strategy

    def getFillStrategy(self):
        """Returns the :class:`pyalgotrade.broker.fillstrategy.FillStrategy` currently set."""
        return self.__fillStrategy

    def getUseAdjustedValues(self):
        return self.__useAdjustedValues

    def setUseAdjustedValues(self, useAdjusted):
        # Deprecated since v0.15
        if not self.__barFeed.barsHaveAdjClose():
            raise Exception("The barfeed doesn't support adjusted close values")
        self.__useAdjustedValues = useAdjusted

    def getActiveOrders(self, instrument=None):
        if instrument is None:
            ret = list(self.__activeOrders.values())
        else:
            ret = [order for order in self.__activeOrders.values() if order.getInstrument() == instrument]
        return ret

    def _getCurrentDateTime(self):
        return self.__barFeed.getCurrentDateTime()

    def getInstrumentTraits(self, instrument):
        return broker.IntegerTraits()

    def getShares(self, instrument):
        return self.__shares.get(instrument, 0)

    def setShares(self, instrument, quantity, price):
        """
        Set existing shares before the strategy starts executing.

        :param instrument: Instrument identifier.
        :param quantity: The number of shares for the given instrument.
        :param price: The price for each share.
        """

        assert not self.__started, "Can't setShares once the strategy started executing"
        self.__shares[instrument] = quantity
        self.__instrumentPrice[instrument] = price

    def getPositions(self):
        return self.__shares

    def getActiveInstruments(self):
        return [instrument for instrument, shares in six.iteritems(self.__shares) if shares != 0]

    def _getPriceForInstrument(self, instrument):
        ret = None

        # Try gettting the price from the last bar first.
        lastBar = self.__barFeed.getLastBar(instrument)
        if lastBar is not None:
            ret = lastBar.getPrice()
        else:
            # Try using the instrument price set by setShares if its available.
            ret = self.__instrumentPrice.get(instrument)

        return ret

    def getEquity(self):
        """Returns the portfolio value (cash + shares * price)."""

        ret = self.get_cash()
        for instrument, shares in six.iteritems(self.__shares):
            instrumentPrice = self._getPriceForInstrument(instrument)
            assert instrumentPrice is not None, "Price for %s is missing" % instrument
            ret += instrumentPrice * shares
        return ret

    # Tries to commit an order execution.
    def commitOrderExecution(self, order, dateTime, fillInfo):
        price = fillInfo.getPrice()
        quantity = fillInfo.getQuantity()

        if order.isBuy():
            cost = price * quantity * -1
            assert (cost < 0)
            sharesDelta = quantity
        elif order.isSell():
            cost = price * quantity
            assert (cost > 0)
            sharesDelta = quantity * -1
        else:  # Unknown action
            assert (False)

        commission = self.getCommission().calculate(order, price, quantity)
        cost -= commission
        resultingCash = self.get_cash() + cost

        # Check that we're ok on cash after the commission.
        if resultingCash >= 0 or self.__allowNegativeCash:

            # Update the order before updating internal state since addExecutionInfo may raise.
            # addExecutionInfo should switch the order state.
            orderExecutionInfo = broker.OrderExecutionInfo(price, quantity, commission, dateTime)
            order.addExecutionInfo(orderExecutionInfo)

            # Commit the order execution.
            self.__cash = resultingCash
            updatedShares = order.getInstrumentTraits().roundQuantity(
                self.getShares(order.getInstrument()) + sharesDelta
            )
            if updatedShares == 0:
                del self.__shares[order.getInstrument()]
            else:
                self.__shares[order.getInstrument()] = updatedShares

            # Let the strategy know that the order was filled.
            self.__fillStrategy.onOrderFilled(self, order)

            # Notify the order update
            if order.isFilled():
                self.unregister_order(order)
                self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.FILLED, orderExecutionInfo))
            elif order.isPartiallyFilled():
                self.notifyOrderEvent(
                    broker.OrderEvent(order, broker.OrderEvent.Type.PARTIALLY_FILLED, orderExecutionInfo)
                )
            else:
                assert (False)
        else:
            self.__logger.debug("Not enough cash to fill %s order [%s] for %s share/s" % (
                order.getInstrument(),
                order.getId(),
                order.getRemaining()
            ))

    def submitOrder(self, order):
        if order.isInitial():
            order.setSubmitted(self._getNextOrderId(), self._getCurrentDateTime())
            self.register_order(order)
            # Switch from INITIAL -> SUBMITTED
            order.switchState(broker.Order.State.SUBMITTED)
            self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.SUBMITTED, None))
        else:
            raise Exception("The order was already processed")

    # Return True if further processing is needed.
    def __preProcessOrder(self, order, bar_):
        ret = True

        # For non-GTC orders we need to check if the order has expired.
        if not order.getGoodTillCanceled():
            expired = bar_.getDateTime().date() > order.getAcceptedDateTime().date()

            # Cancel the order if it is expired.
            if expired:
                ret = False
                self.unregister_order(order)
                order.switchState(broker.Order.State.CANCELED)
                self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.CANCELED, "Expired"))

        return ret

    def __postProcessOrder(self, order, bar_):
        # For non-GTC orders and daily (or greater) bars we need to check if orders should expire right now
        # before waiting for the next bar.
        if not order.getGoodTillCanceled():
            expired = False
            if self.__barFeed.getFrequency() >= pyalgotrade.bar.Frequency.DAY:
                expired = bar_.getDateTime().date() >= order.getAcceptedDateTime().date()

            # Cancel the order if it will expire in the next bar.
            if expired:
                self.unregister_order(order)
                order.switchState(broker.Order.State.CANCELED)
                self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.CANCELED, "Expired"))

    def __processOrder(self, order, bar_):
        if not self.__preProcessOrder(order, bar_):
            return

        # Double dispatch to the fill strategy using the concrete order type.
        fillInfo = order.process(self, bar_)
        if fillInfo is not None:
            self.commitOrderExecution(order, bar_.getDateTime(), fillInfo)

        if order.isActive():
            self.__postProcessOrder(order, bar_)

    def __onBarsImpl(self, order, bars):
        # IF WE'RE DEALING WITH MULTIPLE INSTRUMENTS WE SKIP ORDER PROCESSING IF THERE IS NO BAR FOR THE ORDER'S
        # INSTRUMENT TO GET THE SAME BEHAVIOUR AS IF WERE BE PROCESSING ONLY ONE INSTRUMENT.
        bar_ = bars.getBar(order.getInstrument())
        if bar_ is not None:
            # Switch from SUBMITTED -> ACCEPTED
            if order.isSubmitted():
                order.setAcceptedDateTime(bar_.getDateTime())
                order.switchState(broker.Order.State.ACCEPTED)
                self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.ACCEPTED, None))

            if order.isActive():
                # This may trigger orders to be added/removed from __activeOrders.
                self.__processOrder(order, bar_)
            else:
                # If an order is not active it should be because it was canceled in this same loop and it should
                # have been removed.
                assert (order.isCanceled())
                assert (order not in self.__activeOrders)

    def onBars(self, dateTime, bars):
        # Let the fill strategy know that new bars are being processed.
        self.__fillStrategy.onBars(self, bars)

        # This is to froze the orders that will be processed in this event, to avoid new getting orders introduced
        # and processed on this very same event.
        ordersToProcess = list(self.__activeOrders.values())

        for order in ordersToProcess:
            # This may trigger orders to be added/removed from __activeOrders.
            self.__onBarsImpl(order, bars)

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

    def peekDateTime(self):
        return None

    def createMarketOrder(self, action, instrument, quantity, onClose=False):
        # In order to properly support market-on-close with intraday feeds I'd need to know about different
        # exchange/market trading hours and support specifying routing an order to a specific exchange/market.
        # Even if I had all this in place it would be a problem while paper-trading with a live feed since
        # I can't tell if the next bar will be the last bar of the market session or not.
        if onClose is True and self.__barFeed.isIntraday():
            raise Exception("Market-on-close not supported with intraday feeds")

        return MarketOrder(action, instrument, quantity, onClose, self.getInstrumentTraits(instrument))

    def createLimitOrder(self, action, instrument, limitPrice, quantity):
        return LimitOrder(action, instrument, limitPrice, quantity, self.getInstrumentTraits(instrument))

    def createStopOrder(self, action, instrument, stopPrice, quantity):
        return StopOrder(action, instrument, stopPrice, quantity, self.getInstrumentTraits(instrument))

    def createStopLimitOrder(self, action, instrument, stopPrice, limitPrice, quantity):
        return StopLimitOrder(action, instrument, stopPrice, limitPrice, quantity, self.getInstrumentTraits(instrument))

    def cancelOrder(self, order):
        activeOrder = self.__activeOrders.get(order.getId())
        if activeOrder is None:
            raise Exception("The order is not active anymore")
        if activeOrder.isFilled():
            raise Exception("Can't cancel order that has already been filled")

        self.unregister_order(activeOrder)
        activeOrder.switchState(broker.Order.State.CANCELED)
        self.notifyOrderEvent(
            broker.OrderEvent(activeOrder, broker.OrderEvent.Type.CANCELED, "User requested cancellation")
        )
