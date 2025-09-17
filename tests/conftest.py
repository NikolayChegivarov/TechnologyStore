import pytest
import tempfile
from PIL import Image
from factory import fuzzy
from factory.django import DjangoModelFactory
from django.test import Client
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


@pytest.fixture
def test_manager(db, test_store):
    """Фикстура для создания тестового МЕНЕДЖЕРА"""
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
    """Фикстура для создания тестового ПОКУПАТЕЛЯ"""
    return Customer.objects.create(
        username="test_customer",
        last_name="Петров",
        first_name="Петр",
        middle_name="Петрович",
        email="test@example.com",
        phone="+7 888 888 88 88"
    )


@pytest.fixture
def test_manager_with_user(db, test_store):
    """Фикстура для создания User со статусом Manager"""
    # Сначала создаем менеджера
    manager = Manager.objects.create(
        store=test_store,
        last_name="Иванов",
        first_name="Иван",
        middle_name="Иванович",
        phone="+7 999 999 99 99",
        position="Менеджер"
    )

    # Затем создаем пользователя с ссылкой на менеджера
    user = User.objects.create_user(
        username="test_manager",
        email="manager@example.com",
        password="testpass123",
        role=User.Role.MANAGER,
        first_name="Иван",
        last_name="Иванов",
        manager_profile=manager  # Устанавливаем связь
    )
    return user, manager


@pytest.fixture
def test_customer_with_user(db):
    """Фикстура для создания User со статусом Customer"""
    # Сначала создаем покупателя
    customer = Customer.objects.create(
        username="test_customer",
        last_name="Петров",
        first_name="Петр",
        middle_name="Петрович",
        email="test@example.com",
        phone="+7 888 888 88 88"
    )

    # Затем создаем пользователя с ссылкой на покупателя
    user = User.objects.create_user(
        username="test_customer",
        email="customer@example.com",
        password="testpass123",
        role=User.Role.CUSTOMER,
        first_name="Петр",
        last_name="Петров",
        customer_profile=customer  # Устанавливаем связь
    )
    return user, customer


# @pytest.fixture
# def test_customer(db):
#     """Фикстура для создания тестового покупателя с пользователем"""
#     user = User.objects.create_user(
#         username="test_customer",
#         email="test@example.com",
#         password="testpass123",
#         role=User.Role.CUSTOMER,
#         first_name="Петр",
#         last_name="Петров"
#     )
#     customer = Customer.objects.create(
#         username="test_customer",
#         last_name="Петров",
#         first_name="Петр",
#         middle_name="Петрович",
#         email="test@example.com",
#         phone="+7 888 888 88 88",
#         user_account=user  # Связываем с пользователем
#     )
#     return customer


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


# test_auth_views
@pytest.fixture
def client():
    """Фикстура для Django test client"""
    return Client()


@pytest.fixture
def temp_image():
    """Создает временное изображение для тестов"""
    image = Image.new('RGB', (100, 100), color='red')
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    image.save(tmp_file, 'JPEG')
    tmp_file.seek(0)
    yield tmp_file.name
    tmp_file.close()