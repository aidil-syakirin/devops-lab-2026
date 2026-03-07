from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from .config import Config

print("DATABASE URL:", Config.DATABASE_URL)

# Create database engine
engine = create_engine(
    Config.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

metadata = MetaData()

# Session factory
SessionLocal = scoped_session(
    sessionmaker(bind=engine)
)

# Function to get DB connection
def get_db():
    return engine.connect()
