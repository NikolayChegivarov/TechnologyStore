import pytest
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from store_app.models import Product, Category, Store, Manager


class TestProductModel:
    """Тесты для модели Product"""

    @pytest.mark.django_db
    def test_create_product(self, test_product):
        """Тест создания продукта"""
        assert test_product.name == "Тестовый смартфон"
        assert test_product.price == 29999.99
        assert test_product.available is True
        assert test_product.description == "Описание тестового смартфона"
        assert test_product.category.name == "Смартфоны"
        assert test_product.store.city == "Москва"
        assert test_product.created_by.last_name == "Иванов"

    @pytest.mark.django_db
    def test_product_str_representation(self, test_product):
        """Тест строкового представления продукта"""
        assert str(test_product) == "Тестовый смартфон"

    @pytest.mark.django_db
    def test_product_slug_auto_generation(self, test_category, test_store, test_manager):
        """Тест автоматической генерации slug"""
        product = Product.objects.create(
            category=test_category,
            name="Новый смартфон",
            price=19999.99,
            available=True,
            store=test_store,
            created_by=test_manager
        )

        expected_slug = slugify("Новый смартфон")
        assert product.slug == expected_slug

    @pytest.mark.django_db
    def test_product_slug_uniqueness(self, test_category, test_store, test_manager):
        """Тест уникальности slug"""
        # Создаем первый продукт
        product1 = Product.objects.create(
            category=test_category,
            name="Смартфон X",
            price=29999.99,
            available=True,
            store=test_store,
            created_by=test_manager
        )

        # Создаем второй продукт с таким же именем, но в другом магазине
        store2 = Store.objects.create(city="Санкт-Петербург", address="ул. Другая, д. 2")

        product2 = Product.objects.create(
            category=test_category,
            name="Смартфон X",
            price=39999.99,
            available=True,
            store=store2,
            created_by=test_manager
        )

        # Оба продукта должны иметь одинаковый базовый slug
        base_slug = slugify("Смартфон X")
        assert product1.slug.startswith(base_slug)
        assert product2.slug.startswith(base_slug)

        # Но они должны быть разными
        assert product1.slug != product2.slug

    @pytest.mark.django_db
    def test_product_meta_options(self, test_product):
        """Тест мета-опций продукта"""
        meta = test_product._meta
        assert meta.verbose_name == "Товар"
        assert meta.verbose_name_plural == "Товары"
        assert meta.ordering == ['name', 'price']

    @pytest.mark.django_db
    def test_product_unique_together_constraint(self, test_category, test_store, test_manager):
        """Тест ограничения unique_together (name, store)"""
        Product.objects.create(
            category=test_category,
            name="Уникальный товар",
            price=10000.00,
            available=True,
            store=test_store,
            created_by=test_manager
        )

        # Попытка создать товар с тем же именем в том же магазине должна вызвать ошибку
        with pytest.raises(Exception):  # Может быть IntegrityError
            Product.objects.create(
                category=test_category,
                name="Уникальный товар",
                price=20000.00,
                available=True,
                store=test_store,
                created_by=test_manager
            )

    @pytest.mark.django_db
    def test_product_price_validation(self, test_category, test_store, test_manager):
        """Тест валидации цены"""
        # Создаем необходимые объекты
        store = Store.objects.create(city="Тест", address="ул. Тестовая")
        category = Category.objects.create(name="Тестовая категория", slug="test-category")
        manager = Manager.objects.create(
            store=store,
            last_name="Тестов",
            first_name="Тест",
            phone="+7 000 000 00 00"
        )

        # Отрицательная цена должна вызывать ошибку при full_clean()
        product = Product(
            category=category,
            name="Товар с отрицательной ценой",
            price=-100.00,
            available=True,
            store=store,
            created_by=manager
        )

        # Явно вызываем валидацию
        with pytest.raises(ValidationError):
            product.full_clean()

    @pytest.mark.django_db
    def test_product_available_default(self, test_category, test_store, test_manager):
        """Тест значения по умолчанию для available"""
        product = Product.objects.create(
            category=test_category,
            name="Товар без указания available",
            price=15000.00,
            store=test_store,
            created_by=test_manager
        )
        assert product.available is True

    @pytest.mark.django_db
    def test_product_timestamps(self, test_product):
        """Тест временных меток created_at и updated_at"""
        assert test_product.created_at is not None
        assert test_product.updated_at is not None
        assert test_product.created_at <= test_product.updated_at

    @pytest.mark.django_db
    def test_product_foreign_key_relationships(self, test_product):
        """Тест связей внешних ключей"""
        assert isinstance(test_product.category, Category)
        assert isinstance(test_product.store, Store)
        assert isinstance(test_product.created_by, Manager)

    @pytest.mark.django_db
    def test_product_indexes(self, test_product):
        """Тест наличия индексов"""
        # Проверяем, что индексы определены в мета-классе
        meta = test_product._meta
        index_fields = [index.fields for index in meta.indexes]
        assert ['name', 'price'] in index_fields

    @pytest.mark.django_db
    def test_product_query_by_category(self, test_product, test_category):
        """Тест запросов по категории"""
        products_in_category = Product.objects.filter(category=test_category)
        assert test_product in products_in_category
        assert products_in_category.count() >= 1

    @pytest.mark.django_db
    def test_product_query_by_store(self, test_product, test_store):
        """Тест запросов по магазину"""
        products_in_store = Product.objects.filter(store=test_store)
        assert test_product in products_in_store
        assert products_in_store.count() >= 1

    @pytest.mark.django_db
    def test_product_image_field(self, test_category, test_store, test_manager):
        """Тест поля изображения"""
        product = Product.objects.create(
            category=test_category,
            name="Товар с изображением",
            price=25000.00,
            available=True,
            store=test_store,
            created_by=test_manager,
            image=None  # Допустимо пустое значение
        )
        # Для ImageField нужно проверять не сам объект, а его значение
        assert product.image.name == "" or product.image.name is None

    @pytest.mark.django_db
    def test_product_external_url_field(self, test_category, test_store, test_manager):
        """Тест поля внешней ссылки"""
        product = Product.objects.create(
            category=test_category,
            name="Товар с внешней ссылкой",
            price=35000.00,
            available=True,
            store=test_store,
            created_by=test_manager,
            external_url="https://example.com/product"
        )
        assert product.external_url == "https://example.com/product"