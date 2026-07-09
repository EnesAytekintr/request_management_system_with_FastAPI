import os
import re
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

raw_url = os.getenv('DATABASE_URL')
DATABASE_URL = re.sub(r'^postgresql:', 'postgresql+psycopg:', raw_url) if raw_url else ""

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()