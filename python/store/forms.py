from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control mb-3', 
        'placeholder': 'Nhập địa chỉ Email'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email']
    
    # Can thiệp vào giao diện của các trường Username, Password để thêm class Bootstrap
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-3'})
            self.fields['username'].widget.attrs.update({'placeholder': 'Tên đăng nhập'})
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'price', 'image']
        
        # Thêm class Bootstrap cho đẹp form
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên sản phẩm...'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'duong-dan-seo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả chi tiết...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }