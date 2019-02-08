import abc
import six


@six.add_metaclass(abc.ABCMeta)
class Bar(object):
    """A Bar is a summary of the trading activity for a security in a given period.

    .. note::
        This is a base class and should not be used directly.
    """

    @abc.abstractmethod
    @property
    def use_adjusted_value(self):
        raise NotImplementedError()

    @abc.abstractmethod
    @use_adjusted_value.setter
    def use_adjusted_value(self, use_adjusted):
        raise NotImplementedError()

    @abc.abstractmethod
    @property
    def datetime(self):
        """Returns the :class:`datetime.datetime`."""
        raise NotImplementedError()

    @abc.abstractmethod
    def open(self, adjusted=False):
        """Returns the opening price."""
        raise NotImplementedError()

    @abc.abstractmethod
    def high(self, adjusted=False):
        """Returns the highest price."""
        raise NotImplementedError()

    @abc.abstractmethod
    def low(self, adjusted=False):
        """Returns the lowest price."""
        raise NotImplementedError()

    @abc.abstractmethod
    def close(self, adjusted=False):
        """Returns the closing price."""
        raise NotImplementedError()

    @abc.abstractmethod
    @property
    def volume(self):
        """Returns the volume."""
        raise NotImplementedError()

    @abc.abstractmethod
    @property
    def adj_close(self):
        """Returns the adjusted closing price."""
        raise NotImplementedError()

    @abc.abstractmethod
    @property
    def frequency(self):
        """The bar's period."""
        raise NotImplementedError()

    @property
    def typical_price(self):
        """Returns the typical price."""
        return (self.high() + self.low() + self.close()) / 3.0

    @abc.abstractmethod
    @property
    def price(self):
        """Returns the closing or adjusted closing price."""
        raise NotImplementedError()

    @property
    def extra_columns(self):
        return {}

