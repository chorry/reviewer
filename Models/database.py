from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from Models import *
import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

engine = create_engine('sqlite:///' + config.get('database','dbpath'), convert_unicode=True, echo=False)
db_session = scoped_session(sessionmaker(autocommit=False,
  autoflush=False,
  bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class RepoDB(Base):
  __tablename__ = 'repositories'
  id = Column(Integer, primary_key=True)
  type = Column(String(10), unique=False)
  address = Column(String(500), unique=False)

  def __init__(self, type, address):
    self.type = type
    self.address = address
    return

  def getRepo(self):
    return {'id': str(self.id), 'type': str(self.type), 'address': str(self.address)}

  def __repr__(self):
    return "%s (%r)" % (self.type, self.address)

class ReviewDB(Base):
  __tablename__ = 'reviews'
  id = Column(Integer, primary_key=True)
  type = Column(String(10), unique=False)
  author = Column(String(500), unique=False)
  reviewer = Column(String(500), unique=False)
  state = Column(String(50), unique=False)
  file_count = Column(Integer)

  def __init__(self, type, author, reviewer, items):
    self.type = type
    self.author = author
    self.reviewer = reviewer
    return

  def getItem(self):
    return {'id': str(self.id),
            'type': str(self.type),
            'author': str(self.author),
            'reviewer': self.reviewer,
            'state': self.state,
            'fileCount': self.file_count
    }

class ReviewItemsDB(Base):
  __tablename__ = 'review_items'
  id = Column(Integer, primary_key=True)
  review_id = Column(String(10), unique=False)
  type = Column(String(500), unique=False)
  vcs_id = Column(String(500), unique=False)
  r_from = Column(String(500), unique=False)
  r_to = Column(String(500), unique=False)
  author = Column(String(500), unique=False)
  file_count = Column(Integer)

  def __init__(self, review_id, type, vcs_id, r_from, r_to, author, file_count):
    self.review_id = review_id
    self.type = type
    self.vcs_id = vcs_id
    self.r_from = r_from
    self.r_to = r_to
    self.author = author
    self.file_count = file_count
    return

  def getItem(self):
    return {'id': str(self.id),
            'review_id': str(self.review_id),
            'type': self.type,
            'vcs_id': self.vcs_id,
            'r_from': self.r_from,
            'r_to': self.r_to,
            'author': self.author,
            'file_count': self.file_count
    }

def init_db():
  # import all modules here that might define models so that
  # they will be registered properly on the metadata.  Otherwise
  # you will have to import them first before calling init_db()
  repositories_table = RepoDB.__tablename__
  review_table = ReviewDB.__tablename__
  review_items_table = ReviewItemsDB.__tablename__
  Base.metadata.create_all(bind=engine)