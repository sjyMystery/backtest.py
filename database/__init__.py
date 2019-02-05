from sqlalchemy import Column, DateTime, String, Integer, text,ForeignKey, func,Float,VARCHAR,CHAR,TIMESTAMP
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import cast
from sqlalchemy import event
from sqlalchemy import and_
import time



from config import *

engine = create_engine(f'mysql+mysqldb://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

DBSession = sessionmaker(bind=engine)
Base = declarative_base()


import logging

logging.basicConfig()
logger = logging.getLogger("myapp.sqltime")
logger.setLevel(logging.DEBUG)

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug("Start Query: %s", statement)

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    logger.debug("Query Complete!")
    logger.debug("Total Time: %f", total)
