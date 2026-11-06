"""
Create an engine to start DB connection with postgresql
Create a session to communicate with the engine
Create the Base class
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()
DATABASE_URL = os.getenv(key="DATABASE_URL")
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"
engine = create_engine(DATABASE_URL, echo=SQL_ECHO, hide_parameters=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()