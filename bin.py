from database import db
from pony.orm import *
class Bin(db.Entity):
    type = Required(string)