from .database import SessionLocal
from .models import User

def get_user(user_id: int):
    with SessionLocal() as session:
        return session.query(User).filter(User.id == user_id).first()

def create_user(user_id: int, username: str):
    with SessionLocal() as session:
        user = User(id=user_id, username=username)
        session.add(user)
        session.commit()
        return user