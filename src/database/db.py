import configparser

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

config = configparser.ConfigParser()
config.read('config.ini')

PGUSER = config.get('DB', 'USER')
PGPASS = config.get('DB', 'PASSWORD')
PGHOST = config.get('DB', 'HOST')
PGPORT = config.get('DB', 'PORT')
PGNAME = config.get('DB', 'DB_NAME')

DATABASE_URL = f"postgresql+asyncpg://{PGUSER}:{PGPASS}@{PGHOST}:{PGPORT}/{PGNAME}"
# DATABASE_URL = f"postgresql+asyncpg://{PGUSER}:{PGPASS}@{PGHOST}:{PGPORT}/{PGNAME}"

engine = create_async_engine(DATABASE_URL, echo=True)
# engine = create_engine(DATABASE_URL)
async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


# Base = declarative_base()
# Base.metadata.create_all(bind=engine)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

# Dependency
# async def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         await db.close()
