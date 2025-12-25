from sqlalchemy import *
from database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password_hash = Column(String)
    status = Column(String)

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    category_name = Column(String)

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True)
    category_id = Column(Integer)
    product_name = Column(String)
    description = Column(Text)
    price = Column(Float)
    stock_quantity = Column(Integer)
    status = Column(String)

class CartItem(Base):
    __tablename__ = "cart_items"
    cart_item_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    product_id = Column(Integer)
    quantity = Column(Integer)

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    order_status = Column(String)
    total_amount = Column(Float)

class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    product_id = Column(Integer)
    quantity = Column(Integer)
    price_at_purchase = Column(Float)

class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    amount = Column(Float)
    payment_status = Column(String)

class Review(Base):
    __tablename__ = "reviews"
    review_id = Column(Integer, primary_key=True)
    order_item_id = Column(Integer)
    rating = Column(Integer)
    comment = Column(Text)
