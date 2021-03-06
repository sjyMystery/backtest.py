from datetime import datetime


class Bar:

    def __init__(self, start_date: datetime, end_date: datetime, ask_open: float, ask_close: float, ask_high: float,
                 ask_low: float, bid_open: float, bid_close: float, bid_high: float,
                 bid_low, volume):
        if ask_high < ask_low:
            raise Exception("high < low on %s" % start_date)
        elif ask_high < ask_open:
            raise Exception("high < open on %s" % start_date)
        elif ask_high < ask_close:
            raise Exception("high < close on %s" % start_date)
        elif ask_low > ask_open:
            raise Exception("low > open on %s" % start_date)
        elif ask_low > ask_close:
            raise Exception("low > close on %s" % start_date)

        if bid_high < bid_low:
            raise Exception("high < low on %s" % start_date)
        elif bid_high < bid_open:
            raise Exception("high < open on %s" % start_date)
        elif bid_high < bid_close:
            raise Exception("high < close on %s" % start_date)
        elif bid_low > bid_open:
            raise Exception("low > open on %s" % start_date)
        elif bid_low > bid_close:
            raise Exception("low > close on %s" % start_date)

        self.__start_date = start_date
        self.__end_date = end_date

        self.__ask_open = ask_open
        self.__ask_close = ask_close
        self.__ask_high = ask_high
        self.__ask_low = ask_low

        self.__bid_open = bid_open
        self.__bid_close = bid_close
        self.__bid_high = bid_high
        self.__bid_low = bid_low

        self.__volume = volume

    def __getstate__(self):
        return (
            self.__start_date,
            self.__end_date,
            self.__ask_open,
            self.__ask_close,
            self.__ask_high,
            self.__ask_low,
            self.__bid_open,
            self.__bid_high,
            self.__bid_low,
            self.__bid_close,
            self.__volume,
        )

    @property
    def start_date(self):
        return self.__start_date

    @property
    def end_date(self):
        return self.__end_date

    @property
    def ask_open(self):
        return self.__ask_open

    @property
    def ask_high(self):
        return self.__ask_high

    @property
    def ask_low(self):
        return self.__ask_low

    @property
    def ask_close(self):
        return self.__ask_close

    @property
    def bid_open(self):
        return self.__bid_open

    @property
    def bid_high(self):
        return self.__bid_high

    @property
    def bid_low(self):
        return self.__bid_low

    @property
    def bid_close(self):
        return self.__bid_close

    @property
    def volume(self):
        return self.__volume

    @property
    def price(self):
        return self.__bid_close
