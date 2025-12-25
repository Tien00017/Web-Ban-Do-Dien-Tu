from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class CategoryCreate(BaseModel):
    category_name: str
    parent_id: int | None = None

class ProductCreate(BaseModel):
    category_id: int
    product_name: str
    description: str
    price: float
    stock_quantity: int

class CartAdd(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int

class PaymentCreate(BaseModel):
    order_id: int
    amount: float

class ReviewCreate(BaseModel):
    order_item_id: int
    rating: int
    comment: str
