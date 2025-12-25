from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import CartItem
from schemas import CartAdd

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/")
def add_cart(item: CartAdd, db: Session = Depends(get_db)):
    ci = CartItem(**item.dict(), user_id=1)
    db.add(ci)
    db.commit()
    return ci

@router.get("/")
def get_cart(db: Session = Depends(get_db)):
    return db.query(CartItem).all()
