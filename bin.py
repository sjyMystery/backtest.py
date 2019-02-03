from database import *

Base = declarative_base()


class Bin(Base):
    __tablename__='user'
    id = Column(Integer,primary_key=True)
    type = Column(String(20),primary_key=True)

    ask_open = Column(Float)
    ask_low = Column(Float)
    ask_heigh = Column(Float)
    ask_close = Column(Float)

    bid_open = Column(Float)
    bid_low = Column(Float)
    bid_heigh = Column(Float)
    bid_close = Column(Float)

    start_date = Column(DateTime,primary_key=True)
    end_time = Column(DateTime,primary_key=True)


new_bin = Bin(id=1,type='EURUSR',end_date=DateTime('2012/01/01 00:00:00.000'),start_date=DateTime('2012/01/01 00:00:00.000'))