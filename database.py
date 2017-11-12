from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import settings

engine = create_engine(settings.database_url, echo=settings.database_debug_output)

Base = declarative_base()


def get_db_session():
    session_factory = sessionmaker(bind=engine)
    db_session = scoped_session(session_factory)
    return db_session


def init_db():
    import models
    db_session = get_db_session()
    Base.metadata.create_all(bind=engine)
    node_all = models.Node(id=models.NodeType.ALL.value)
    node_materials = models.Node(id=models.NodeType.MATERIAL.value, parent=node_all)
    node_events = models.Node(id=models.NodeType.EVENT.value, parent=node_all)
    node_topics = models.Node(id=models.NodeType.TOPIC.value, parent=node_all)
    node_news = models.Node(id=models.NodeType.NEWS.value, parent=node_all)
    db_session.add_all((node_all, node_materials, node_events, node_topics, node_news))
    db_session.commit()
