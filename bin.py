from database import *
import datetime



class Bin(Base):
    __tablename__='bins'
    id = Column(Integer,primary_key=True)
    type = Column(String(20))

    ask_open = Column(Float)
    ask_low = Column(Float)
    ask_high = Column(Float)
    ask_close = Column(Float)

    bid_open = Column(Float)
    bid_low = Column(Float)
    bid_high = Column(Float)
    bid_close = Column(Float)

    start_date = Column(DateTime)
    end_date = Column(DateTime)

    @staticmethod
    def fetch(type,to_date=datetime.datetime(2019,1,1,0,0,0),from_date=datetime.datetime(2012,1,1,0,0,0)):
        '''
            选择一段时间的交易记录，并且返回
            from_date: 开始时间
            to_date: 结束时间
            type: 种类
        '''
        session = DBSession()
        result = session.query(Bin).filter(Bin.type == type).filter(Bin.start_date>=from_date).filter(Bin.end_date<=to_date).all()
        session.close()
        return result

    
    