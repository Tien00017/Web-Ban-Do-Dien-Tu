from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Payment
from schemas import PaymentCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/")
def pay(p: PaymentCreate, db: Session = Depends(get_db)):
    pay = Payment(order_id=p.order_id, amount=p.amount, payment_status="PAID")
    db.add(pay)
    db.commit()
    return pay
