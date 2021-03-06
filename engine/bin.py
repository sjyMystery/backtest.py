from database import *
import datetime



class Bin(Base):
    __tablename__='bins'
    id = Column(Integer,primary_key=True)
    type = Column(CHAR(45))

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
        result = session.query(Bin).filter(and_(\
            cast(Bin.type,String) == cast(type,String),\
            func.timestamp(Bin.start_date)>=func.timestamp(from_date),\
            func.timestamp(Bin.end_date) <= func.timestamp(to_date))).all()
        session.close()
        return result

    def serialize():
        return {
            "ask_open":self.ask_open,
            "ask_low":self.ask_low,
            "ask_high":self.ask_high,
            "ask_close":self.ask_close,
            "bid_open":self.bid_open,
            "bid_low":self.bid_low,
            "bid_high":self.bid_high,
            "bid_close":self.bid_close,
            "type":self.type,
            "start_date":self.start_date,
            "end_date":self.end_date,
            "id":self.id
        }