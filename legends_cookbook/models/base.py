from sqlalchemy import inspect
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

from .ingredient import init_table as init_ingredients

def init_tables_data(SessionLocal):
    init_ingredients(SessionLocal)

def check_or_create_tables(engine):
    # Create the tables in the database
    if not inspect(engine).has_table('ingredients'):
        Base.metadata.create_all(bind=engine)