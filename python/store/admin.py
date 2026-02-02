from django.contrib import admin
from .models import Category, Product, Order, OrderItem

# Đăng ký các model đơn giản
admin.site.register(Category)
admin.site.register(Product)

# Tạo bảng phụ để xem chi tiết sản phẩm trong đơn hàng
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

# Đăng ký model Order với giao diện tùy chỉnh
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Lưu ý: Các tên trường ở đây PHẢI KHỚP với file models.py
    list_display = ['id', 'full_name', 'phone', 'total_price', 'complete', 'created_at']
    list_filter = ['complete', 'created_at']
    search_fields = ['id', 'full_name', 'phone', 'email']
    inlines = [OrderItemInline]