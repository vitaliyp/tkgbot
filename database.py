from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///data.sqlite3', echo=True)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()
Base.query = Session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
