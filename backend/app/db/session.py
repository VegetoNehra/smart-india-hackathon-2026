from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# We use SQLite for the hackathon MVP for ease of use.
# It can easily be swapped out for PostgreSQL via this URL later.
SQLALCHEMY_DATABASE_URL = "sqlite:///./monsoon.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
