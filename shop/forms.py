from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'price', 'description', 'image']  # Removed 'category'
        widgets = {
            'product_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique product ID (e.g., LAP001)',
                'maxlength': '20'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price (e.g., 99.99)',
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product description...',
                'rows': 4
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        
    def clean_product_id(self):
        product_id = self.cleaned_data['product_id']
        if Product.objects.filter(product_id=product_id).exists():
            raise forms.ValidationError("This product ID already exists. Please choose a different one.")
        return product_id
        
    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")
        return price