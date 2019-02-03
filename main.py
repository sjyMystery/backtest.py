from bin import Bin
from database import *
import datetime

bin1 = Bin(type='EURUSD',start_time=datetime.datetime(2015,1,1,0,0,0))

session = DBSession()

result = session.query(bin1).all()
print(result)