from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# We are using SQLite. It creates a single file named 'app.db' in your folder.
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# This is a helper function to safely open and close database connections
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()