from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import create_engine

DP_URL = 'postgresql://postgres:admin@localhost/agro_ai'

engine = create_engine(DP_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
