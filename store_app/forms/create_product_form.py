# В файле forms.py
from django import forms
from ..models import Product, Category, Store


class CreatProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'available', 'store']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

        labels = {
            'category': 'Категория',
            'name': 'Название товара',
            'description': 'Описание',
            'price': 'Цена',
            'available': 'Доступен для продажи',
            'store': 'Магазин'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Выберите категорию"
        self.fields['store'].empty_label = "Выберите магазин"