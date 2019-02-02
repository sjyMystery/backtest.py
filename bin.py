from pony.orm import *



class Bin:
    def __init__(self,instrument,start_time,end_time,ask_open,ask_low,ask_heigh,ask_close,bid_open,bid_low,bid_heigh,bid_close):
        self.start_time = start_time
        self.end_time = end_time
        self.ask_open = self.ask_open
        self.ask_low = self.ask_low
        self.ask_heigh = self.ask_heigh
        self.ask_close = self.ask_close
        self.instrument = self.instrument
        self.bid_open = self.bid_open
        self.bid_low = self.bid_low
        self.bid_heigh = self.bid_heigh
        self.bid_close = self.bid_close
        