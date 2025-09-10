import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from store_app.models import Product, Category, Store, Manager


@pytest.mark.django_db
class TestProductModel:
    """Тесты для модели Product"""

    def test_product_creation(self, create_product):
        """Тест создания продукта"""
        product = create_product(name="iPhone 15", price=999.99)

        assert product.name == "iPhone 15"
        assert product.price == 999.99
        assert product.available == True
        assert product.slug is not None
        assert "iphone-15" in product.slug

    def test_product_with_image(self, create_product):
        """Тест создания продукта с изображением"""
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        product = create_product(
            name="Samsung Galaxy",
            price=899.99,
            with_image=True
        )

        assert product.image is not None
        assert "test_image" in product.image.name

    def test_product_with_external_url(self, create_product):
        """Тест создания продукта с внешней ссылкой"""
        product = create_product(
            name="Xiaomi Phone",
            price=499.99
        )
        product.external_url = "https://example.com/product/123"
        product.save()

        assert product.external_url == "https://example.com/product/123"

    def test_product_slug_generation(self, create_product):
        """Тест автоматической генерации slug"""
        product1 = create_product(name="Тестовый товар", price=100.00)
        product2 = create_product(name="Тестовый товар", price=200.00)
        product3 = create_product(name="Другой товар", price=300.00)

        assert product1.slug == "testovyi-tovar"
        assert product2.slug == "testovyi-tovar-1"  # Уникальный slug
        assert product3.slug == "drugoi-tovar"

    def test_product_cyrillic_slug(self, create_product):
        """Тест генерации slug из кириллических названий"""
        product = create_product(name="Смартфон Самсунг", price=500.00)

        assert product.slug == "smartfon-samsung"
        assert product.slug.isascii()  # Slug должен содержать только латинские символы

    def test_product_price_validation(self, create_product):
        """Тест валидации цены"""
        # Отрицательная цена должна вызывать ошибку
        with pytest.raises(ValidationError):
            product = create_product(price=-100.00)
            product.full_clean()

        # Нулевая цена
        with pytest.raises(ValidationError):
            product = create_product(price=0.00)
            product.full_clean()

        # Корректная цена
        product = create_product(price=100.00)
        product.full_clean()  # Не должно быть ошибки

    def test_product_availability(self, create_product):
        """Тест изменения доступности товара"""
        product = create_product(name="Available Product", price=100.00)
        assert product.available == True

        product.available = False
        product.save()
        assert product.available == False

    def test_product_string_representation(self, create_product):
        """Тест строкового представления"""
        product = create_product(name="MacBook Pro", price=1999.99)

        assert str(product) == "MacBook Pro"
        assert product.name in str(product)

    def test_product_meta_options(self, create_product):
        """Тест мета-опций модели"""
        assert Product._meta.verbose_name == "Товар"
        assert Product._meta.verbose_name_plural == "Товары"
        assert Product._meta.ordering == ['name', 'price']

    def test_product_unique_together(self, create_product, create_store):
        """Тест уникальности названия в рамках магазина"""
        store1 = create_store(city="Москва")
        store2 = create_store(city="Санкт-Петербург")

        # Товары с одинаковым названием в разных магазинах - OK
        product1 = create_product(name="Same Product", price=100.00, store=store1)
        product2 = create_product(name="Same Product", price=100.00, store=store2)

        assert product1.name == product2.name
        assert product1.store != product2.store

    def test_product_foreign_key_relationships(self, create_product, create_category, create_store, create_manager):
        """Тест связей с другими моделями"""
        category = create_category(name="Ноутбуки")
        store = create_store(city="Екатеринбург")
        manager = create_manager(first_name="Анна", last_name="Сидорова")

        product = create_product(
            name="Dell XPS",
            price=1500.00,
            category=category,
            store=store,
            created_by=manager
        )

        assert product.category == category
        assert product.store == store
        assert product.created_by == manager
        assert product in category.products.all()
        assert product in store.products.all()
        assert product in manager.products_created.all()

    def test_product_save_method(self, create_product):
        """Тест метода save"""
        product = Product(
            name="New Product Without Slug",
            price=200.00,
            available=True
        )

        # Slug должен быть создан при сохранении
        assert product.slug is None
        product.save()
        assert product.slug is not None
        assert "new-product-without-slug" in product.slug

    def test_product_indexes(self, create_product):
        """Тест наличия индексов"""
        indexes = [index.fields for index in Product._meta.indexes]
        assert ['name', 'price'] in indexes
        assert Product._meta.get_field('slug').db_index == True

    def test_product_decimal_places(self, create_product):
        """Тест точности decimal поля"""
        product = create_product(price=123.4567)  # Больше 2 знаков после запятой

        # Цена должна быть округлена до 2 знаков
        assert product.price == 123.46

    def test_product_with_special_characters(self, create_product):
        """Тест названия со специальными символами"""
        product = create_product(name="Product #1 with @special! chars", price=50.00)

        # Slug должен корректно обрабатывать специальные символы
        assert "product-1-with-special-chars" in product.slug

    def test_product_blank_fields(self, create_product):
        """Тест необязательных полей"""
        product = create_product(description="")  # Пустое описание
        product.external_url = None  # Null внешняя ссылка

        # Не должно быть ошибок валидации
        product.full_clean()

        assert product.description == ""
        assert product.external_url is None
