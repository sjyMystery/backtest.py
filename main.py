from bin import Bin
from database import *
import datetime


result = Bin.select('AUDCAD',from_date=datetime.datetime(2012,1,1,0,0,0),to_date=datetime.datetime(2012,1,5,0,0,0))

