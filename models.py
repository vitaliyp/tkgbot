from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from database import Base
import enum


class NodeType(enum.Enum):
    ALL = 0
    TOPIC = -1
    MATERIAL = -2 
    EVENT = -3
    SECTION = -4
    OTHER = -5


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    node_id = Column(Integer, ForeignKey('nodes.id'), nullable=False)
    node = relationship('Node', back_populates='subscriptions')
    top_level_only = Column(Boolean, nullable=False, default=False)
    new_entries = Column(Boolean, nullable=False, default=True)
    new_entries_only = Column(Boolean, nullable=False, default=False)
    exception = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return ('<Subscription(chat_id=%s, node_id=%s, top_level_only=%s, '
                'new_entries=%s, new_entries_only=%s exception=%s)>'%(
                self.chat_id, self.node_id, self.top_level_only, 
                self.new_entries, self.exception, self.new_entries_only))


class Node(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    last_checked = Column(DateTime) 
    subscriptions = relationship('Subscription', back_populates='node')
    parent_id = Column(Integer, ForeignKey('nodes.id'))
    children = relationship('Node', backref=backref('parent', remote_side=[id]))

    def __repr__(self):
        return '<Node(name=%s, last_checked=%s, parent_id=%)>'%(
                self.name, self.last_checked, self.parent_id)
