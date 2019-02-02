from pony.orm import *
from config import *

db = Database()

db.bind('mysql',host=f'{db_host}',user=db_name,passwd=db_password,db=db_name)

print('hi')