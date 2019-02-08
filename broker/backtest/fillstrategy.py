import abc
import six

from order import Order, Action
from broker.backtest.order import MarketOrder, LimitOrder, StopLimitOrder, StopOrder
from bar import Bar, Frequency, Bars
from broker.backtest.backtest import Broker
import broker.backtest.slippage as slippage
import broker.backtest.backtest as backtest


# Returns the trigger price for a Limit or StopLimit order, or None if the limit price was not yet penetrated.
def get_limit_price_trigger(action: Action, price: float, use_adjusted_values, bar: Bar):
    ret = None
    open_ = bar.open(use_adjusted_values)
    high = bar.high(use_adjusted_values)
    low = bar.low(use_adjusted_values)

    # If the bar is below the limit price, use the open price.
    # If the bar includes the limit price, use the open price or the limit price.
    if action in [Action.BUY, Action.BUY_TO_COVER]:
        if high < price:
            ret = open_
        elif price >= low:
            if open_ < price:  # The limit price was penetrated on open.
                ret = open_
            else:
                ret = price
    # If the bar is above the limit price, use the open price.
    # If the bar includes the limit price, use the open price or the limit price.
    elif action in [Action.SELL, Action.SELL_SHORT]:
        if low > price:
            ret = open_
        elif price <= high:
            if open_ > price:  # The limit price was penetrated on open.
                ret = open_
            else:
                ret = price
    else:  # Unknown action
        assert False
    return ret


# Returns the trigger price for a Stop or StopLimit order, or None if the stop price was not yet penetrated.
def get_stop_price_trigger(action: Action, price: float, use_adjusted_values, bar: Bar):
    ret = None
    open_ = bar.open(use_adjusted_values)
    high = bar.high(use_adjusted_values)
    low = bar.low(use_adjusted_values)

    # If the bar is above the stop price, use the open price.
    # If the bar includes the stop price, use the open price or the stop price. Whichever is better.
    if action in [Action.BUY, Action.BUY_TO_COVER]:
        if low > price:
            ret = open_
        elif price <= high:
            if open_ > price:  # The stop price was penetrated on open.
                ret = open_
            else:
                ret = price
    # If the bar is below the stop price, use the open price.
    # If the bar includes the stop price, use the open price or the stop price. Whichever is better.
    elif action in [Action.SELL, Action.SELL_SHORT]:
        if high < price:
            ret = open_
        elif price >= low:
            if open_ < price:  # The stop price was penetrated on open.
                ret = open_
            else:
                ret = price
    else:  # Unknown action
        assert False

    return ret


class FillInfo(object):
    def __init__(self, price: float, quantity: float):
        self.__price = price
        self.__quantity = quantity

    @property
    def price(self):
        return self.__price

    @property
    def quantity(self):
        return self.__quantity


@six.add_metaclass(abc.ABCMeta)
class FillStrategy(object):
    """Base class for order filling strategies for the backtester."""

    def on_bars(self, broker_: Broker, bars):
        pass

    def on_order_filled(self, broker_: Broker, order_: Order):
        pass

    @abc.abstractmethod
    def fill_market_order(self, broker_: Broker, order_: Order, bar_: Bar):
        raise NotImplementedError()

    @abc.abstractmethod
    def fill_limit_order(self, broker_: Broker, order_: Order, bar_: Bar):
        raise NotImplementedError()

    @abc.abstractmethod
    def fill_stop_order(self, broker_: Broker, order_: Order, bar: Bar):
        raise NotImplementedError()

    @abc.abstractmethod
    def fill_stop_limit_order(self, broker_: Broker, order: Order, bar: Bar):
        raise NotImplementedError()


class DefaultStrategy(FillStrategy):
    """
    Default fill strategy.

    :param volumeLimit: The proportion of the volume that orders can take up in a bar. Must be > 0 and <= 1.
        If None, then volume limit is not checked.
    :type volumeLimit: float

    This strategy works as follows:

    * A :class:`order.MarketOrder` is always filled using the open/close price.
    * A :class:`order.LimitOrder` will be filled like this:
        * If the limit price was penetrated with the open price, then the open price is used.
        * If the bar includes the limit price, then the limit price is used.
        * Note that when buying the price is penetrated if it gets <= the limit price, and when selling the price
          is penetrated if it gets >= the limit price
    * A :class:`order.StopOrder` will be filled like this:
        * If the stop price was penetrated with the open price, then the open price is used.
        * If the bar includes the stop price, then the stop price is used.
        * Note that when buying the price is penetrated if it gets >= the stop price, and when selling the price
          is penetrated if it gets <= the stop price
    * A :class:`order.StopLimitOrder` will be filled like this:
        * If the stop price was penetrated with the open price, or if the bar includes the stop price, then the limit
          order becomes active.
        * If the limit order is active:
            * If the limit order was activated in this same bar and the limit price is penetrated as well, then the
              best between the stop price and the limit fill price (as described earlier) is used.
            * If the limit order was activated at a previous bar then the limit fill price (as described earlier)
              is used.

    .. note::
        * This is the default strategy used by the Broker.
        * It uses :class:`order.slippage.NoSlippage` slippage model by default.
        * If volumeLimit is 0.25, and a certain bar's volume is 100, then no more than 25 shares can be used by all
          orders that get processed at that bar.
        * If using trade bars, then all the volume from that bar can be used.
    """

    def __init__(self, volume_limit=0.25):
        super(DefaultStrategy, self).__init__()
        self.__volumeLeft = {}
        self.__volumeUsed = {}
        self.__volumeLimit = volume_limit
        self.__slippageModel = slippage.NoSlippage()

    def on_bars(self, broker_: Broker, bars: Bars):
        volume_left = {}

        for instrument in bars.instruments:
            bar = bars[instrument]
            # Reset the volume available for each instrument.
            if bar.frequency == Frequency.TRADE:
                volume_left[instrument] = bar.volume
            elif self.__volumeLimit is not None:
                # We can't round here because there is no order to request the instrument traits.
                volume_left[instrument] = bar.volume * self.__volumeLimit
            # Reset the volume used for each instrument.
            self.__volumeUsed[instrument] = 0.0

        self.__volumeLeft = volume_left

    @property
    def volume_left(self):
        return self.__volumeLeft

    @property
    def volume_used(self):
        return self.__volumeUsed

    def on_order_filled(self, broker_: Broker, order_: Order):
        # Update the volume left.
        if self.__volumeLimit is not None:
            # We round the volume left here because it was not rounded when it was initialized.
            volume_left = order_.instrument_traits.roundQuantity(self.__volumeLeft[order_.instrument])
            fill_quantity = order_.filled
            assert volume_left >= fill_quantity, \
                "Invalid fill quantity %s. Not enough volume left %s" % (fill_quantity, volume_left)
            self.__volumeLeft[order_.instrument] = order_.instrument_traits.roundQuantity(
                volume_left - fill_quantity
            )

        # Update the volume used.
        self.__volumeUsed[order_.instrument] = order_.instrument_traits.roundQuantity(
            self.__volumeUsed[order_.instrument] + order_.quantity
        )

    @property
    def volume_limit(self):
        return self.__volumeLimit

    @volume_limit.setter
    def volume_limit(self, value):
        """
        Set the volume limit.

        :param value: The proportion of the volume that orders can take up in a bar. Must be > 0 and <= 1.
            If None, then volume limit is not checked.
        :type value: float
        """

        if value is not None:
            assert 1 >= value > 0 and "Invalid volume limit"

        self.__volumeLimit = value

    def __calculate_fill_size(self, broker_: Broker, order: Order, bar: Bar):
        ret = 0

        # If self.__volumeLimit is None then allow all the order to get filled.
        if self.__volumeLimit is not None:
            max_volume = self.__volumeLeft.get(order.instrument, 0)
            max_volume = order.instrument_traits.roundQuantity(max_volume)
        else:
            max_volume = order.remain

        if not order.all_or_one:
            ret = min(max_volume, order.remain)
        elif order.remain <= max_volume:
            ret = order.remain

        return ret

    def fill_market_order(self, broker_: Broker, order: MarketOrder, bar: Bar):
        # Calculate the fill size for the order.
        fill_size = self.__calculate_fill_size(broker_, order, bar)
        if fill_size == 0:
            broker_.logger.debug(
                "Not enough volume to fill %s market order [%s] for %s share/s" % (
                    order.instrument,
                    order.id,
                    order.remain
                )
            )
            return None

        # Unless its a fill-on-close order, use the open price.
        if order.fill_on_close:
            price = bar.close(broker_.use_adjusted_values)
        else:
            price = bar.open(broker_.use_adjusted_values)
        assert price is not None

        # Don't slip prices when the bar represents the trading activity of a single trade.
        if bar.frequency != Frequency.TRADE:
            price = self.__slippageModel.calculate_price(
                order, price, fill_size, bar, self.__volumeUsed[order.instrument]
            )
        return FillInfo(price, fill_size)

    def fill_limit_order(self, broker_: Broker, order_: LimitOrder, bar: Bar):
        # Calculate the fill size for the order.
        fill_size = self.__calculate_fill_size(broker_, order_, bar)
        if fill_size == 0:
            broker_.logger.debug("Not enough volume to fill %s limit order [%s] for %s share/s" % (
                order_.instrument, order_.id, order_.remain))
            return None
        ret = None
        price = get_limit_price_trigger(order_.action, order_.price, broker_.use_adjusted_values, bar)
        if price is not None:
            ret = FillInfo(price, fill_size)
        return ret

    def fill_stop_order(self, broker_: Broker, order_: StopOrder, bar: Bar):
        ret = None
        # First check if the stop price was hit so the market order becomes active.
        price_trigger = None
        if not order_:
            price_trigger = get_stop_price_trigger(
                order_.action,
                order_.price,
                broker_.use_adjusted_values,
                bar
            )
            order_.stop_hit = (price_trigger is not None)

        # If the stop price was hit, check if we can fill the market order.
        if order_.stop_hit:
            # Calculate the fill size for the order.
            fill_size = self.__calculate_fill_size(broker_, order_, bar)
            if fill_size == 0:
                broker_.logger.debug("Not enough volume to fill %s stop order [%s] for %s share/s" % (
                    order_.instrument,
                    order_.id,
                    order_.remain
                ))
                return None

            # If we just hit the stop price we'll use it as the fill price.
            # For the remaining bars we'll use the open price.
            if price_trigger is not None:
                price = price_trigger
            else:
                price = bar.open(broker_.use_adjusted_values)
            assert price is not None

            # Don't slip prices when the bar represents the trading activity of a single trade.
            if bar.frequency != Frequency.TRADE:
                price = self.__slippageModel.calculate_price(
                    order_, price, fill_size, bar, self.__volumeUsed[order_.instrument]
                )
            ret = FillInfo(price, fill_size)
        return ret

    def fill_stop_limit_order(self, broker_: Broker, order: StopLimitOrder, bar: Bar):
        ret = None

        # First check if the stop price was hit so the limit order becomes active.
        price_trigger = None
        if not order.stop_hit:
            price_trigger = get_stop_price_trigger(
                order.action,
                order.stop_price,
                broker_.use_adjusted_values,
                bar
            )
            order.stop_hit = (price_trigger is not None)

        # If the stop price was hit, check if we can fill the limit order.
        if order.stop_hit:
            # Calculate the fill size for the order.
            fill_size = self.__calculate_fill_size(broker_, order, bar)
            if fill_size == 0:
                broker_.logger.debug("Not enough volume to fill %s stop limit order [%s] for %s share/s" % (
                    order.instrument,
                    order.id,
                    order.remain
                ))
                return None

            price = get_limit_price_trigger(
                order.action,
                order.limit_price,
                broker_.use_adjusted_values,
                bar
            )
            if price is not None:
                # If we just hit the stop price, we need to make additional checks.
                if price_trigger is not None:
                    if order.is_buy:
                        # If the stop price triggered is lower than the limit price, then use that one.
                        # Else use the limit price.
                        price = min(price_trigger, order.limit_price)
                    else:
                        # If the stop price triggered is greater than the limit price, then use that one.
                        # Else use the limit price.
                        price = max(price_trigger, order.limit_price)

                ret = FillInfo(price, fill_size)

        return ret
