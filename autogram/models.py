from sqlalchemy import Column, Boolean, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'
  
  id = Column(Integer, primary_key=True)
  is_bot = Column(Boolean, default=False)   # todo: Check if non-bot update can be received
  first_name = Column(String)
  username = Column(String)
  language_code = Column(String)

class Channel(Base):
  __tablename__ = 'channel'
  
  id = Column(Integer, primary_key=True)
  title = Column(String)
  username = Column(String)
  status = Column(String)
  rights = Column(String)

class Supergroup(Base):
  __tablename__ = 'supergroup'
  
  id = Column(Integer, primary_key=True)
  title = Column(String)
  status = Column(String)
  rights = Column(String, nullable=True)

class Update(Base):
  __tablename__ = 'update'
  
  id = Column(Integer, primary_key=True)
  date = Column(Integer)
  data = Column(String)
  bot_id = Column(Integer, ForeignKey('bot.id'))
  bot = relationship('BotBase', back_populates='updates')

class BotBase(Base):
  __tablename__ = 'bot'
  
  id = Column(Integer, primary_key=True)
  first_name = Column(String)
  username = Column(String)
  can_join_groups = Column(Boolean)
  can_read_all_group_messages = Column(Boolean, default=False)
  supports_inline_queries = Column(Boolean, default=False)
  
  #relations
  updates = relationship('Update', back_populates='bot')
  
  def __init__(self):
    self.engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(self.engine)


__all__ = [
	'Base', 'BotBase', 'User', 'Supergroup', 'Update'
]
