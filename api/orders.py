from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Order
from schemas import OrderCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/")
def create_order(o: OrderCreate, db: Session = Depends(get_db)):
    order = Order(user_id=o.user_id, order_status="PENDING", total_amount=0)
    db.add(order)
    db.commit()
    return order

@router.get("/")
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()
