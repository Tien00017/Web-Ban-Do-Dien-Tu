from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Review
from schemas import ReviewCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/")
def add_review(r: ReviewCreate, db: Session = Depends(get_db)):
    review = Review(**r.dict())
    db.add(review)
    db.commit()
    return review

@router.get("/")
def get_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()
