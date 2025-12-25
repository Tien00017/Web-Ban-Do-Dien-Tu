from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Category
from schemas import CategoryCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/")
def create_category(cat: CategoryCreate, db: Session = Depends(get_db)):
    c = Category(**cat.dict())
    db.add(c)
    db.commit()
    return c

@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()
