def cart_total(request):
    cart = request.session.get('cart', {})
    return {'cart_count': sum(cart.values())}
# File: store/context_processors.py

def cart_count_global(request):
    cart = request.session.get('cart', {})
    # Tính tổng số lượng (Ví dụ: 2 chuột + 1 phím = 3)
    # cart.values() là danh sách số lượng của từng món
    count = sum(cart.values()) 
    return {'cart_count': count}