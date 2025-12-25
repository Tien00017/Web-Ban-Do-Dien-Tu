from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Product
from schemas import ProductCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/")
def create_product(p: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**p.dict(), status="ACTIVE")
    db.add(product)
    db.commit()
    return product

@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
