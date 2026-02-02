from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    # 11 nhãn: cables, case, cpu, gpu, hdd, headset, keyboard, monitor, motherboard, mouse, ram
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    
    def __str__(self): return self.name
    class Meta: verbose_name_plural = 'Categories'

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5) # 1-5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- CÁC TRƯỜNG MỚI CẦN THÊM ---
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    # -------------------------------
    
    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Đơn hàng {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=0) # Giá tại thời điểm mua

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    
    @property
    def get_total(self):
        return self.price * self.quantity