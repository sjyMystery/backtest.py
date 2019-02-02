from pony.orm import *
from config import *
db.bind('mysql',host=f'{db_host}:{db_port}',user=db_name,passwd=db_password,db=db_name)