from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import SessionLocal

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
