from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Review, Order, OrderItem
from django.contrib.auth.decorators import login_required
from .ai_utils import predict_image_class
from django.contrib import messages
from django.db.models import Q
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ProductForm  # Import cái form vừa tạo
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order

def home(request):
    products = Product.objects.filter(available=True).order_by('-created')[:20]
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'products': products, 'categories': categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all().order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
        return redirect('product_detail', slug=slug)
        
    return render(request, 'store/detail.html', {'product': product, 'reviews': reviews})

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'products': products, 'categories': categories, 'curr_cat': category})

def search(request):
    categories = Category.objects.all() # Cần dòng này để không bị mất menu
    query = request.GET.get('q', '')
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        products = Product.objects.none()

    return render(request, 'store/home.html', {
        'products': products, 
        'categories': categories,
        'search_query': query
    })

# ... các import khác ...

def search_ai(request):
    if request.method == 'POST' and request.FILES.get('image'):
        img = request.FILES['image']
        try:
            # 1. AI nhận diện (Kết quả trả về là Tiếng Anh)
            # Ví dụ: 'monitor', 'keyboard', 'mouse', 'graphics_card'...
            ai_label_english = predict_image_class(img) 
            
            if ai_label_english:
                # Chuyển về chữ thường để dễ so sánh
                label_clean = ai_label_english.lower().strip()
                
                # 2. BỘ TỪ ĐIỂN DỊCH (Anh -> Database của bạn)
                # Bên trái: Từ AI trả về (dựa trên class của model bạn dùng)
                # Bên phải: Từ khóa để tìm trong Database (Phải khớp với tên sản phẩm bạn đã tạo)
                TRANSLATION_MAP = {
                    # Màn hình
                    'monitor': 'Màn hình',
                    'screen': 'Màn hình',
                    'television': 'Màn hình',
                    'display': 'Màn hình',
                    
                    # Chuột & Phím
                    'mouse': 'Chuột',
                    'computer mouse': 'Chuột',
                    'keyboard': 'Bàn phím',
                    'computer keyboard': 'Bàn phím',
                    'space bar': 'Bàn phím',
                    
                    # Linh kiện bên trong
                    'graphics card': 'GPU',
                    'video card': 'GPU',
                    'gpu': 'GPU',
                    'cpu': 'CPU',
                    'processor': 'CPU',
                    'chip': 'CPU',
                    'motherboard': 'Mainboard',
                    'mainboard': 'Mainboard',
                    'ram': 'RAM',
                    'memory': 'RAM',
                    'hard disk': 'HDD',
                    'hard drive': 'HDD',
                    'disk drive': 'HDD',
                    
                    # Khác
                    'desktop computer': 'Case', # Thường AI nhìn case nó hay đoán là desktop
                    'tower': 'Case',
                    'computer case': 'Case',
                    'laptop': 'Laptop',
                    'joystick': 'Tay cầm',
                }

                # 3. Dịch từ khóa
                # Nếu từ AI có trong từ điển thì lấy từ tiếng Việt, không thì giữ nguyên
                search_term = TRANSLATION_MAP.get(label_clean, label_clean)

                # Hiển thị thông báo cho người dùng hiểu
                messages.success(request, f"AI nhận diện: {ai_label_english} -> Tìm kiếm: {search_term}")

                # 4. Tìm kiếm trong Database theo từ khóa ĐÃ DỊCH
                # Tìm trong tên danh mục HOẶC tên sản phẩm
                products = Product.objects.filter(
                    Q(category__name__icontains=search_term) | 
                    Q(name__icontains=search_term)
                )
                
                categories = Category.objects.all()
                return render(request, 'store/home.html', {
                    'products': products, 
                    'categories': categories,
                    'search_query': f"Kết quả AI: {search_term}"
                })

        except Exception as e:
            print(f"AI Error: {e}")
            messages.error(request, "Lỗi khi xử lý ảnh hoặc model chưa load được")
            
    return redirect('home')

# --- CART LOGIC (SESSION) ---
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1
    request.session['cart'] = cart
    try:
        product = Product.objects.get(id=product_id)
        msg = f"Đã thêm {product.name} vào giỏ!"
    except:
        msg = "Đã thêm vào giỏ!"
    # -------------------------------------------

    messages.success(request, msg)
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def view_cart(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0
    for p in products:
        qty = cart[str(p.id)]
        subtotal = p.price * qty
        total += subtotal
        cart_items.append({'product': p, 'qty': qty, 'subtotal': subtotal})
    
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart')

@login_required
def checkout(request):
    # 1. Lấy giỏ hàng từ session
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    # 2. Tính toán lại tiền (Giống hệt bên hàm view_cart)
    for p_id, qty in cart.items():
        try:
            product = Product.objects.get(id=p_id)
            subtotal = product.price * qty
            total_price += subtotal
            
            cart_items.append({
                'product': product,
                'qty': qty,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            continue

    # 3. Xử lý khi người dùng bấm nút "XÁC NHẬN ĐẶT HÀNG" (POST)
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        email = request.POST.get('email')
        note = request.POST.get('note')

        if not cart_items:
            messages.error(request, "Giỏ hàng trống!")
            return redirect('home')

        # Tạo đơn hàng (Order)
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=name,
            phone=phone,
            address=address,
            email=email,
            note=note,
            total_price=total_price
        )

        # Tạo chi tiết đơn hàng (OrderItem)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['product'].price,
                quantity=item['qty']
            )

        # Xóa giỏ hàng
        del request.session['cart']
        
        # --- SỬA DÒNG NÀY ---
        # Cũ: return redirect('home')
        # Mới: Chuyển sang trang cảm ơn kèm theo ID đơn hàng
        return redirect('order_success', order_id=order.id)

    # 4. Gửi dữ liệu ra giao diện (Đây là bước quan trọng để hiện số tiền)
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'store/checkout.html', context)

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/dashboard.html', {'orders': orders})
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Đăng ký xong tự động đăng nhập luôn
            messages.success(request, f"Đăng ký thành công! Xin chào {user.username}")
            return redirect('home')
        else:
            messages.error(request, "Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.")
    else:
        form = RegistrationForm()
        
    return render(request, 'store/register.html', {'form': form})
def search(request):
    query = request.GET.get('q', '') # Lấy từ khóa người dùng nhập
    if query:
        # Tìm kiếm theo tên sản phẩm HOẶC mô tả (không phân biệt hoa thường)
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        products = Product.objects.none() # Nếu không nhập gì thì không hiện gì

    return render(request, 'store/home.html', {'products': products, 'search_query': query})
def order_success(request, order_id):
    # Lấy đơn hàng vừa đặt để hiện thông tin
    order = get_object_or_404(Order, id=order_id)
    
    return render(request, 'store/order_success.html', {
        'order': order
    })
def is_admin(user):
    return user.is_superuser

# 1. Trang Dashboard Quản lý (READ)
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    products = Product.objects.all().order_by('-id') # Sản phẩm mới nhất lên đầu
    orders = Order.objects.all().order_by('-created_at') # Đơn hàng mới nhất lên đầu
    
    context = {
        'products': products,
        'orders': orders,
        'total_orders': orders.count(),
        'total_products': products.count()
    }
    return render(request, 'store/admin_dashboard.html', context)

# 2. Thêm sản phẩm (CREATE)
@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES) # request.FILES để upload ảnh
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm sản phẩm thành công!")
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Thêm sản phẩm mới'})

# 3. Sửa sản phẩm (UPDATE)
@login_required
@user_passes_test(is_admin)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật thành công!")
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Sửa sản phẩm'})

# 4. Xóa sản phẩm (DELETE)
@login_required
@user_passes_test(is_admin)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Đã xóa sản phẩm!")
        return redirect('admin_dashboard')
    
    return render(request, 'store/product_confirm_delete.html', {'product': product})
# 1. Trang danh sách thành viên
@login_required
@user_passes_test(is_admin)
def manage_users(request):
    # Lấy tất cả user (trừ bản thân người đang đăng nhập để tránh lỡ tay xóa nhầm mình)
    users = User.objects.all().order_by('-date_joined')
    
    return render(request, 'store/manage_users.html', {'users': users})

# 2. Xóa thành viên
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    
    # Không cho phép xóa Superuser (Admin) để bảo mật
    if user_to_delete.is_superuser:
        messages.error(request, "Không thể xóa tài khoản Admin!")
    else:
        user_to_delete.delete()
        messages.success(request, "Đã xóa tài khoản thành công!")
        
    return redirect('manage_users')
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # --- PHẦN QUAN TRỌNG: PHÂN LUỒNG ---
                if user.is_superuser:
                    # Nếu là Admin -> Chuyển thẳng vào trang quản trị
                    return redirect('admin_dashboard') 
                else:
                    # Nếu là Khách -> Về trang chủ mua hàng
                    return redirect('home') 
                # -----------------------------------
                
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'store/login.html', {'form': form})
# --- 1. QUẢN LÝ USER ---
@staff_member_required(login_url='login')
def manage_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'store/manage_users.html', {'users': users})

@staff_member_required(login_url='login')
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    # Không cho phép xóa chính mình (Admin đang đăng nhập)
    if user_to_delete != request.user:
        user_to_delete.delete()
        messages.success(request, f"Đã xóa user {user_to_delete.username}")
    else:
        messages.error(request, "Không thể tự xóa tài khoản admin đang đăng nhập!")
    return redirect('manage_users')

# --- 2. QUẢN LÝ ĐƠN HÀNG ---
@staff_member_required(login_url='login')
def manage_orders(request):
    # Lấy tất cả đơn hàng, mới nhất lên đầu
    orders = Order.objects.all().order_by('-created_at') 
    return render(request, 'store/manage_orders.html', {'orders': orders})

@staff_member_required(login_url='login')
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Đảo ngược trạng thái: Nếu chưa xong -> Xong, và ngược lại
    order.complete = not order.complete
    order.save()
    status = "Đã hoàn thành" if order.complete else "Chưa xử lý"
    messages.success(request, f"Đơn hàng #{order.id} chuyển sang trạng thái: {status}")
    return redirect('manage_orders')