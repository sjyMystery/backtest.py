from bin import Bin
from database import *
import datetime

bin1 = Bin(type='EURUSD',start_date=datetime.datetime(2015,1,1,0,0,0))

session = DBSession()

result = session.query(Bin).filter(Bin.type=='EURUSD').filter(Bin.start_date==datetime.datetime(2015,1,1,0,0,0)).one()