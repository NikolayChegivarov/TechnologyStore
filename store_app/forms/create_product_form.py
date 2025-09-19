# В файле forms.py
from django import forms
from ..models import Product, Category, Store


class CreateProductForm(forms.ModelForm):
    # Явно определяем поле external_url с параметром assume_scheme
    external_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'https://example.com'}),
        label='Ссылка на товар'
    )

    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'available', 'store', 'image', 'external_url']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),  # Добавлен min
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
            # УБЕРИТЕ external_url отсюда, так как он уже определен выше
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Выберите категорию"
        self.fields['store'].empty_label = "Выберите магазин"

        # Убедимся, что поле price имеет правильные атрибуты
        self.fields['price'].widget.attrs.update({
            'step': '0.01',
            'min': '0.01'
        })