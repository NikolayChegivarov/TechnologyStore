import pytest
from django.contrib.auth import get_user_model
from store_app.models import Store, Category, Manager, Customer, Product

User = get_user_model()

# Models/Product
@pytest.fixture
def test_store(db):
    """Фикстура для создания тестового магазина"""
    return Store.objects.create(
        city="Москва",
        address="ул. Тестовая, д. 1"
    )


@pytest.fixture
def test_category(db):
    """Фикстура для создания тестовой категории"""
    return Category.objects.create(
        name="Смартфоны",
        slug="smartfony"
    )


@pytest.fixture
def test_manager(db, test_store):
    """Фикстура для создания тестового менеджера"""
    return Manager.objects.create(
        store=test_store,
        last_name="Иванов",
        first_name="Иван",
        middle_name="Иванович",
        phone="+7 999 999 99 99",
        position="Менеджер"
    )


@pytest.fixture
def test_customer(db):
    """Фикстура для создания тестового покупателя"""
    return Customer.objects.create(
        username="test_customer",
        last_name="Петров",
        first_name="Петр",
        middle_name="Петрович",
        email="test@example.com",
        phone="+7 888 888 88 88"
    )


@pytest.fixture
def test_product(db, test_category, test_store, test_manager):
    """Фикстура для создания тестового продукта"""
    return Product.objects.create(
        category=test_category,
        name="Тестовый смартфон",
        description="Описание тестового смартфона",
        price=29999.99,
        available=True,
        store=test_store,
        created_by=test_manager
    )

