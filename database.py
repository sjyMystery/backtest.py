from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func,Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_


from config import *

engine = create_engine(f'mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

DBSession = sessionmaker(bind=engine)

Base = declarative_base()

