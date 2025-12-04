from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fake_users_db = []

class UserInfo(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(user: UserInfo):
    for u in fake_users_db:
        if u["username"] == username:
            raise HTTPException(status_code=400, detail="User đã tồn tại")
    
    hashed_pass = pwd_context.hash(user.password)
    fake_users_db.append({"username": user.username, "password": hashed_pass})
    return{"message": "Đăng ký thành công", "user": user.username}

# API ĐĂNG NHẬP
@router.post("/login")
def login(user: UserInfo):
    found_user = next((u for u in fake_users_db if u["username"] == user.username))
    
    if not found_user or not pwd_context.verify(user.password, found_user["password"]):
        raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")
    
    return{"message": "Đăng nhập thành công", "token": "fake-jwt-token-xyz"}
