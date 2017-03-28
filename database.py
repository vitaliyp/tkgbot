from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import settings


engine = create_engine(settings.database_url, echo=settings.database_debug_output)
session_factory = sessionmaker(bind=engine)
db_session = scoped_session(session_factory)

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
