from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.infrastructure.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# For SQLite, we should enable foreign key support if possible, but let's keep it simple first
# as per the warning in refactor_context.md

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
