from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_view, name='category_detail'),
    path('search-ai/', views.search_ai, name='search_ai'),
    
    path('add-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('search/', views.search, name='search'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('custom-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/add/', views.add_product, name='add_product'),
    path('custom-admin/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('custom-admin/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('custom-admin/users/', views.manage_users, name='manage_users'),
    path('custom-admin/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('custom-admin/orders/', views.manage_orders, name='manage_orders'),
    path('custom-admin/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
]