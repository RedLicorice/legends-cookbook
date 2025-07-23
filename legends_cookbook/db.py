import socket
import logging
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from .config import settings
from .models.base import check_or_create_tables, init_tables_data

#Wait DB to be online
def wait_for_mysql(host: str, port: int, timeout: int = 60):
    start_time = time.time()
    logging.info(f"Waiting MySQL server at {host}:{port}")
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                logging.info("MySQL is online")
                return True
        except (OSError, ConnectionRefusedError):
            if time.time() - start_time >= timeout:
                raise TimeoutError(f"Could not connect to MySQL server at {host}:{port} within {timeout} seconds")
            logging.info(f"Waiting for MySQL to become online at {host}:{port}...")
            time.sleep(2)
    return False

def wait_for_db():
    if settings.database.mode == 'sqlite':
        logging.info("Using SQLite DB Mode. No ping needed.")
        return True
    return wait_for_mysql(settings.database.locale.host, settings.database.locale.port)

SessionLocal = None

def connect_mysql_db():
    global SessionLocal
    # Database connection settings
    DATABASE_URL = f"mysql+pymysql://{settings.database.locale.username}:{settings.database.locale.password}@{settings.database.locale.host}:{str(settings.database.locale.port)}/{settings.database.locale.schema}"

    # SQLAlchemy setup
    engine = create_engine(DATABASE_URL, pool_pre_ping=True) # Utilizzare il parametro pool_pre_ping per verificare la connessione prima di ogni utilizzo.
    
    check_or_create_tables(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    init_tables_data(SessionLocal)

    logging.info("MySQL db connected!")

def connect_sqlite_db():
    global SessionLocal
    dbfile = settings.database.sqlite.filename
    if not dbfile:
        dbfile = ':memory:'
    engine = create_engine(f"sqlite:///{dbfile}", connect_args=dict(check_same_thread=False))
    
    check_or_create_tables(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    init_tables_data(SessionLocal)
    
    logging.info("SQLite db connected!")

def connect_db():
    if settings.database.mode == 'mysql':
        connect_mysql_db()
    else:
        connect_sqlite_db()
        

# Dependency to get DB session on FastAPI
def get_db():
    if not SessionLocal:
        logging.error("Database not connected yet.")
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# For NiceGUI
# Use: 
#       with db_session() as db:
#           users = UserService().get_users(db)
@contextmanager
def db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()