# В файле forms.py
from django import forms
from ..models import Product, Category, Store


class CreateProductForm(forms.ModelForm):  # Исправлено название класса
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'available', 'store', 'image', 'external_url']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'external_url': forms.URLInput(
                attrs={
                    'placeholder': 'https://example.com'
                }
            ),
        }

        labels = {
            'category': 'Категория',
            'name': 'Название товара',
            'description': 'Описание',
            'price': 'Цена',
            'available': 'Доступен для продажи',
            'store': 'Магазин',
            'image': 'Фотография товара',
            'external_url': 'Ссылка на товар'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Выберите категорию"
        self.fields['store'].empty_label = "Выберите магазин"

        # Явно задаем схему для external_url field
        self.fields['external_url'].widget.attrs['assume_scheme'] = 'https'