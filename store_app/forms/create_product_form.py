# В файле forms.py
from django import forms
from ..models import Product, Category, Store


class CreateProductForm(forms.ModelForm):
    # Явно определяем поле external_url с параметром assume_scheme
    external_url = forms.URLField(
        required=False,
        assume_scheme='https',  # Добавляем параметр здесь
        widget=forms.URLInput(attrs={'placeholder': 'https://example.com'})
    )

    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'available', 'store', 'image', 'external_url']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            # Убираем external_url из widgets, так как определили его выше
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