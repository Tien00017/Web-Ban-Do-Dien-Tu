from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# -------------------------------------
# HOME
# -------------------------------------
@app.get("/")
def home():
    return {"message": "API giỏ hàng đã chạy thành công!"}


# -------------------------------------
# MÔ TẢ SẢN PHẨM GỬI LÊN API
# -------------------------------------
class AddToCart(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int = 1


# -------------------------------------
# GIỎ HÀNG LƯU TRONG RAM
# -------------------------------------
cart = []


# -------------------------------------
# API: THÊM SẢN PHẨM VÀO GIỎ
# -------------------------------------
@app.post("/cart/add")
def add_to_cart(item: AddToCart):
    cart.append(item.model_dump())   # convert object → dict

    return {
        "message": "Đã thêm vào giỏ!",
        "cart": cart
    }


# -------------------------------------
# API: XEM GIỎ HÀNG
# -------------------------------------
@app.get("/cart")
def get_cart():
    return {
        "cart": cart,
        "total_items": sum(item["quantity"] for item in cart),
        "total_price": sum(item["price"] * item["quantity"] for item in cart)
    }


# -------------------------------------
# API: XÓA 1 SẢN PHẨM THEO product_id
# -------------------------------------
@app.delete("/cart/remove/{product_id}")
def remove_item(product_id: int):
    global cart
    new_cart = [item for item in cart if item["product_id"] != product_id]

    if len(new_cart) == len(cart):
        return {"message": "Không tìm thấy sản phẩm để xóa!"}

    cart = new_cart
    return {
        "message": "Đã xóa sản phẩm!",
        "cart": cart
    }


# -------------------------------------
# API: XÓA TOÀN BỘ GIỎ
# -------------------------------------
@app.delete("/cart/clear")
def clear_cart():
    cart.clear()
    return {
        "message": "Giỏ hàng đã được làm trống!",
        "cart": cart
    }
