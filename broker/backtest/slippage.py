import abc
import six

from order import Order
from bar import Bar


@six.add_metaclass(abc.ABCMeta)
class SlippageModel(object):
    """Base class for slippage models.

    .. note::
        This is a base class and should not be used directly.
    """

    @abc.abstractmethod
    def calculate_price(self, order: Order, price: float, quantity: float, bar: Bar, volume_used: float):
        """
        Returns the slipped price per share for an order.

        :param order: The order being filled.
        :type order: :class:`order.Order`.
        :param price: The price for each share before slippage.
        :type price: float.
        :param quantity: The amount of shares that will get filled at this time for this order.
        :type quantity: float.
        :param bar: The current bar.
        :type bar: :class:`order.bar.Bar`.
        :param volume_used: The volume size that was taken so far from the current bar.
        :type volume_used: float.
        :rtype: float.
        """
        raise NotImplementedError()


class NoSlippage(SlippageModel):
    """A no slippage model."""

    def calculate_price(self, order: Order, price: float, quantity: float, bar: Bar, volume_used: float):
        return price


class VolumeShareSlippage(SlippageModel):
    """
    A volume share slippage model as defined in Zipline's VolumeShareSlippage model.
    The slippage is calculated by multiplying the price impact constant by the square of the ratio of the order
    to the total volume.

    Check https://www.quantopian.com/help#ide-slippage for more details.

    :param price_impact: Defines how large of an impact your order will have on the backtester's price calculation.
    :type price_impact: float.
    """

    def __init__(self, price_impact=0.1):
        super(VolumeShareSlippage, self).__init__()
        self.__priceImpact = price_impact

    def calculate_price(self, order: Order, price: float, quantity: float, bar: Bar, volume_used: float):
        assert bar.volume, "Can't use 0 volume bars with VolumeShareSlippage"

        total_volume = volume_used + quantity
        volume_share = total_volume / float(bar.volume)
        impact_pct = volume_share ** 2 * self.__priceImpact
        if order.is_buy:
            ret = price * (1 + impact_pct)
        else:
            ret = price * (1 - impact_pct)
        return ret
