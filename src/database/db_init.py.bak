from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path

Base = declarative_base()

class Improvement(Base):
    __tablename__ = 'improvements'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    improvement_type = Column(String)
    original_code = Column(String)
    improved_code = Column(String)
    description = Column(String)
    extra_data = Column(JSON)
    status = Column(String)

def init_db(db_path: str = 'improvements.db'):
    # Ensure the database directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session() 