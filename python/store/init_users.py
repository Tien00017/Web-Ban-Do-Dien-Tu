from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Tự động tạo Superuser và User thường để test'

    def handle(self, *args, **kwargs):
        self.stdout.write("⏳ Đang tiến hành tạo tài khoản...")

        # --- 1. TẠO SUPERUSER (ADMIN) ---
        admin_name = 'admin1python manage.py init_users'
        admin_pass = '123'
        
        if not User.objects.filter(username=admin_name).exists():
            User.objects.create_superuser(
                username=admin_name,
                email='admin@gmail.com',
                password=admin_pass
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Đã tạo Superuser: {admin_name} / Pass: {admin_pass}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Superuser "{admin_name}" đã tồn tại, bỏ qua.'))

        # --- 2. TẠO USER THƯỜNG (KHÁCH HÀNG) ---
        user_name = 'khachhang'
        user_pass = '123'
        
        if not User.objects.filter(username=user_name).exists():
            User.objects.create_user(
                username=user_name,
                email='khach@gmail.com',
                password=user_pass
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Đã tạo User thường: {user_name} / Pass: {user_pass}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  User "{user_name}" đã tồn tại, bỏ qua.'))