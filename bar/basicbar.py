from bar.bar import Bar
from datetime import datetime


class BasicBar(Bar):
    # Optimization to reduce memory footprint.
    __slots__ = (
        '__dateTime',
        '__open',
        '__close',
        '__high',
        '__low',
        '__volume',
        '__adjClose',
        '__frequency',
        '__useAdjustedValue',
        '__extra',
    )

    def __init__(self, datetime_: datetime, open_, high, low, close, volume, adj_close, frequency, extra={}):
        if high < low:
            raise Exception("high < low on %s" % datetime_)
        elif high < open_:
            raise Exception("high < open on %s" % datetime_)
        elif high < close:
            raise Exception("high < close on %s" % datetime_)
        elif low > open_:
            raise Exception("low > open on %s" % datetime_)
        elif low > close:
            raise Exception("low > close on %s" % datetime_)

        self.__dateTime = datetime_
        self.__open = open_
        self.__close = close
        self.__high = high
        self.__low = low
        self.__volume = volume
        self.__adjClose = adj_close
        self.__frequency = frequency
        self.__useAdjustedValue = False
        self.__extra = extra

    def __setstate__(self, state):
        (self.__dateTime,
         self.__open,
         self.__close,
         self.__high,
         self.__low,
         self.__volume,
         self.__adjClose,
         self.__frequency,
         self.__useAdjustedValue,
         self.__extra) = state

    def __getstate__(self):
        return (
            self.__dateTime,
            self.__open,
            self.__close,
            self.__high,
            self.__low,
            self.__volume,
            self.__adjClose,
            self.__frequency,
            self.__useAdjustedValue,
            self.__extra
        )

    @property
    def use_adjusted_value(self):
        return self.__useAdjustedValue

    @use_adjusted_value.setter
    def use_adjusted_value(self, use_adjusted):
        if use_adjusted and self.__adjClose is None:
            raise Exception("Adjusted close is not available")
        self.__useAdjustedValue = use_adjusted

    @property
    def datetime(self):
        return self.__dateTime

    def open(self, adjusted=False):
        if adjusted:
            if self.__adjClose is None:
                raise Exception("Adjusted close is missing")
            return self.__adjClose * self.__open / float(self.__close)
        else:
            return self.__open

    def high(self, adjusted=False):
        if adjusted:
            if self.__adjClose is None:
                raise Exception("Adjusted close is missing")
            return self.__adjClose * self.__high / float(self.__close)
        else:
            return self.__high

    def low(self, adjusted=False):
        if adjusted:
            if self.__adjClose is None:
                raise Exception("Adjusted close is missing")
            return self.__adjClose * self.__low / float(self.__close)
        else:
            return self.__low

    def close(self, adjusted=False):
        if adjusted:
            if self.__adjClose is None:
                raise Exception("Adjusted close is missing")
            return self.__adjClose
        else:
            return self.__close

    @property
    def volume(self):
        return self.__volume

    @property
    def adj_close(self):
        return self.__adjClose

    @property
    def frequency(self):
        return self.__frequency

    @property
    def price(self):
        if self.__useAdjustedValue:
            return self.__adjClose
        else:
            return self.__close

    @property
    def extra_columns(self):
        return self.__extra
