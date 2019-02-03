from bin import Bin
from database import *
import datetime


result = Bin.select('EURUSD',datetime.datetime(2018,1,1,0,0,0),datetime.datetime(2018,1,5,0,0,0))
print(result)