import configparser

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


config = configparser.ConfigParser()
config.read('config.ini')

PGUSER = config.get('DB', 'USER')
PGPASS = config.get('DB', 'PASSWORD')
PGHOST = config.get('DB', 'HOST')
PGPORT = config.get('DB', 'PORT')
PGNAME = config.get('DB', 'DB_NAME')

DATABASE_URL = f"postgresql://{PGUSER}:{PGPASS}@{PGHOST}:{PGPORT}/{PGNAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
