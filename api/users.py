from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from schemas import UserCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    u = User(
        username=user.username,
        email=user.email,
        password_hash=user.password,
        status="ACTIVE"
    )
    db.add(u)
    db.commit()
    return u

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
