# В файле forms.py
from django import forms
from ..models import Product, Category, Store


class CreatProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'available', 'store']

        # Добавляем русские названия полей
        labels = {
            'category': 'Категория',
            'name': 'Название товара',
            'description': 'Описание',
            'price': 'Цена',
            'available': 'Доступен для продажи',
            'store': 'Магазин'
        }

        # Дополнительно можно настроить виджеты для лучшего отображения
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введите описание товара'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }