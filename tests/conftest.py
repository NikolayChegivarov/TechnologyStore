import pytest
import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from store_app.models import Store, Category, Manager, Customer, Product, User


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

# test_user_models.py
@pytest.fixture
def test_store():
    """Фикстура для создания тестового магазина"""
    return Store.objects.create(
        city="Москва",
        address="ул. Тестовая, д. 1"
    )


@pytest.fixture
def test_manager(test_store):
    """Фикстура для создания тестового менеджера"""
    return Manager.objects.create(
        store=test_store,
        last_name="Иванов",
        first_name="Петр",
        middle_name="Сергеевич",
        phone="+7 999 123 45 67",
        position="Менеджер по продажам"
    )


@pytest.fixture
def test_customer():
    """Фикстура для создания тестового покупателя"""
    return Customer.objects.create(
        username="test_customer",
        last_name="Петров",
        first_name="Иван",
        middle_name="Васильевич",
        email="test@example.com",
        phone="+7 999 765 43 21",
        address="ул. Покупательская, д. 10"
    )


@pytest.fixture
def test_admin_user():
    """Фикстура для создания тестового пользователя с ролью ADMIN"""
    return User.objects.create_user(
        username="admin_user",
        password="testpass123",
        first_name="Админ",
        last_name="Системный",
        role=User.Role.ADMIN
    )


@pytest.fixture
def test_manager_user(test_manager):
    """Фикстура для создания тестового пользователя с ролью MANAGER"""
    user = User.objects.create_user(
        username="manager_user",
        password="testpass123",
        first_name=test_manager.first_name,
        last_name=test_manager.last_name,
        role=User.Role.MANAGER,
        manager_profile=test_manager
    )
    return user


@pytest.fixture
def test_customer_user(test_customer):
    """Фикстура для создания тестового пользователя с ролью CUSTOMER"""
    user = User.objects.create_user(
        username="customer_user",
        password="testpass123",
        first_name=test_customer.first_name,
        last_name=test_customer.last_name,
        role=User.Role.CUSTOMER,
        customer_profile=test_customer
    )
    return user


# test_auth_views
@pytest.fixture
def customer_user(db):
    """Фикстура создания тестового пользователя с ролью CUSTOMER"""
    return User.objects.create_user(
        email='customer@test.com',
        password='testpass123',
        username='customer_user',
        role=User.Role.CUSTOMER
    )

@pytest.fixture
def manager_user(db):
    """Фикстура создания тестового пользователя с ролью MANAGER"""
    return User.objects.create_user(
        email='manager@test.com',
        password='testpass123',
        username='manager_user',
        role=User.Role.MANAGER
    )

@pytest.fixture
def admin_user(db):
    """Фикстура создания тестового пользователя с ролью ADMIN"""
    return User.objects.create_user(
        email='admin@test.com',
        password='testpass123',
        username='admin_user',
        role=User.Role.ADMIN
    )

