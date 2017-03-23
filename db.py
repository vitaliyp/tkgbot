from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy import Table, Column, MetaData
from sqlalchemy import ForeignKey

import sqlalchemy

engine = sqlalchemy.create_engine('sqlite:///data.db', echo=True)

metadata = MetaData()
metadata.bind = engine

subscriptions = Table('subscriptions', metadata,
    Column('id', Integer, primary_key=True),
    Column('chat_id', Integer, nullable=False),
    Column('node', None, ForeignKey('nodes.id')),
    Column('new_topics', Boolean, nullable=False),
)

nodes = Table('nodes', metadata,
    Column('id', Integer, primary_key=True),
    Column('last_updated', DateTime, nullable=True),
    Column('name', String, nullable=True),
    Column('topic', Boolean, nullable=True),
)

metadata.create_all(engine)
