from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import settings

engine = create_engine(settings.database_url, echo=settings.database_debug_output)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    import models
    Base.metadata.create_all(bind=engine)

    node_all = models.Node(id=models.NodeType.ALL.value)
    node_sections = models.Node(id=models.NodeType.SECTION.value, parent=node_all)
    node_materials = models.Node(id=models.NodeType.MATERIAL.value, parent=node_all)
    node_events = models.Node(id=models.NodeType.EVENT.value, parent=node_all)
    node_topics = models.Node(id=models.NodeType.TOPIC.value, parent=node_all)
    node_news = models.Node(id=models.NodeType.NEWS.value, parent=node_all)

    with session_scope() as session:
        session.add_all((node_all, node_sections, node_materials, node_events, node_topics, node_news))
