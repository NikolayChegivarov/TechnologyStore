import pytest
from django import forms
from store_app.forms.create_product_form import CreateProductForm
from store_app.models import Product, Category, Store


@pytest.mark.django_db
class TestCreateProductForm:
    """Тесты для формы CreateProductForm"""

    @pytest.fixture
    def test_category(self, db):
        """Фикстура для тестовой категории"""
        return Category.objects.create(
            name="Тестовая категория",
            slug="test-category"
        )

    @pytest.fixture
    def test_store(self, db):
        """Фикстура для тестового магазина"""
        return Store.objects.create(
            city="Москва",
            address="ул. Тестовая, д. 1"
        )

    def test_create_product_form_fields(self):
        """Тест наличия всех полей в форме"""
        form = CreateProductForm()
        expected_fields = [
            'category', 'name', 'description', 'price',
            'available', 'store', 'image', 'external_url'
        ]
        for field in expected_fields:
            assert field in form.fields

    def test_create_product_form_field_types(self):
        """Тест типов полей формы"""
        form = CreateProductForm()

        assert isinstance(form.fields['category'], forms.ModelChoiceField)
        assert isinstance(form.fields['name'], forms.CharField)
        assert isinstance(form.fields['description'], forms.CharField)
        assert isinstance(form.fields['price'], forms.DecimalField)
        assert isinstance(form.fields['available'], forms.BooleanField)
        assert isinstance(form.fields['store'], forms.ModelChoiceField)
        assert isinstance(form.fields['image'], forms.ImageField)
        assert isinstance(form.fields['external_url'], forms.URLField)

    def test_create_product_form_widget_attrs(self):
        """Тест атрибутов виджетов"""
        form = CreateProductForm()

        description_widget = form.fields['description'].widget
        assert description_widget.attrs['rows'] == 3

        price_widget = form.fields['price'].widget
        assert price_widget.attrs['step'] == '0.01'

        external_url_widget = form.fields['external_url'].widget
        assert external_url_widget.attrs['placeholder'] == 'https://example.com'

    def test_create_product_form_labels(self):
        """Тест меток полей"""
        form = CreateProductForm()

        assert form.fields['category'].label == 'Категория'
        assert form.fields['name'].label == 'Название товара'
        assert form.fields['description'].label == 'Описание'
        assert form.fields['price'].label == 'Цена'
        assert form.fields['available'].label == 'Доступен для продажи'
        assert form.fields['store'].label == 'Магазин'
        assert form.fields['image'].label == 'Фотография товара'
        assert form.fields['external_url'].label == 'Ссылка на товар'

    def test_create_product_form_empty_labels(self, test_category, test_store):
        """Тест пустых меток для выпадающих списков"""
        form = CreateProductForm()

        assert form.fields['category'].empty_label == "Выберите категорию"
        assert form.fields['store'].empty_label == "Выберите магазин"

    def test_create_product_form_valid_data(self, test_category, test_store):
        """Тест валидных данных"""
        form_data = {
            'category': test_category.id,
            'name': 'Тестовый товар',
            'description': 'Описание тестового товара',
            'price': '1000.00',
            'available': True,
            'store': test_store.id,
            'external_url': 'https://example.com/product'
        }
        form = CreateProductForm(data=form_data)
        assert form.is_valid()

    def test_create_product_form_required_fields(self, test_category, test_store):
        """Тест обязательных полей"""
        # Все поля кроме external_url и image обязательны
        form_data = {
            'category': test_category.id,
            'name': 'Тестовый товар',
            'description': 'Описание тестового товара',
            'price': '1000.00',
            'available': True,
            'store': test_store.id,
        }
        form = CreateProductForm(data=form_data)
        assert form.is_valid()

    def test_create_product_form_missing_required_fields(self):
        """Тест отсутствия обязательных полей"""
        form_data = {
            'name': 'Тестовый товар',
            # Пропущены category, price, store
        }
        form = CreateProductForm(data=form_data)
        assert not form.is_valid()
        assert 'category' in form.errors
        assert 'price' in form.errors
        assert 'store' in form.errors

    def test_create_product_form_invalid_price(self, test_category, test_store):
        """Тест невалидной цены"""
        form_data = {
            'category': test_category.id,
            'name': 'Тестовый товар',
            'description': 'Описание тестового товара',
            'price': '-100.00',  # Отрицательная цена
            'available': True,
            'store': test_store.id,
        }
        form = CreateProductForm(data=form_data)
        assert not form.is_valid()
        assert 'price' in form.errors

    def test_create_product_form_invalid_url(self, test_category, test_store):
        """Тест невалидного URL"""
        form_data = {
            'category': test_category.id,
            'name': 'Тестовый товар',
            'description': 'Описание тестового товара',
            'price': '1000.00',
            'available': True,
            'store': test_store.id,
            'external_url': 'invalid-url'  # Невалидный URL
        }
        form = CreateProductForm(data=form_data)
        assert not form.is_valid()
        assert 'external_url' in form.errors

    def test_create_product_form_external_url_optional(self, test_category, test_store):
        """Тест что external_url не обязателен"""
        form_data = {
            'category': test_category.id,
            'name': 'Тестовый товар',
            'description': 'Описание тестового товара',
            'price': '1000.00',
            'available': True,
            'store': test_store.id,
            # external_url отсутствует
        }
        form = CreateProductForm(data=form_data)
        assert form.is_valid()

    def test_create_product_form_image_optional(self, test_category, test_store):
        """Тест что image не обязателен"""
        form_data = {
            'category': test_category.id,
            'name': 'Тестовый товар',
            'description': 'Описание тестового товара',
            'price': '1000.00',
            'available': True,
            'store': test_store.id,
        }
        form = CreateProductForm(data=form_data)
        assert form.is_valid()

    def test_create_product_form_save(self, test_category, test_store):
        """Тест сохранения формы"""
        form_data = {
            'category': test_category.id,
            'name': 'Тестовый товар для сохранения',
            'description': 'Описание тестового товара',
            'price': '1500.00',
            'available': True,
            'store': test_store.id,
            'external_url': 'https://example.com/test-product'
        }
        form = CreateProductForm(data=form_data)
        assert form.is_valid()

        product = form.save(commit=False)
        assert product.name == 'Тестовый товар для сохранения'
        assert product.price == 1500.00
        assert product.available == True
        assert product.external_url == 'https://example.com/test-product'
        assert product.category == test_category
        assert product.store == test_store