from fastapi import FastAPI
from database import Base, engine
from routers import users, categories, products, cart, orders, payments, reviews

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Electronic Store Backend API")

app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
