# filepath: init_db.py
from db.database import engine
from db.models import Base

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()