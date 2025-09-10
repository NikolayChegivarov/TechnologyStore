import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from store_app.models import (
    User, Customer, Manager, Store, Category, Product,
    FavoriteProduct, CartItem, Order, OrderItem, ActionLog
)
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Автоматически предоставляет доступ к БД для всех тестов"""
    pass


@pytest.fixture
def client():
    """Фикстура для тестового клиента"""
    return Client()


@pytest.fixture
def create_store():
    """Создание магазина"""

    def make_store(city="Москва", address="ул. Примерная, д. 1"):
        return Store.objects.create(city=city, address=address)

    return make_store


@pytest.fixture
def create_category():
    """Создание категории"""

    def make_category(name="Электроника", slug=None):
        if slug is None:
            slug = slugify(name)
        return Category.objects.create(name=name, slug=slug)

    return make_category


@pytest.fixture
def create_manager(create_store):
    """Создание менеджера"""

    def make_manager(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            phone="+79991234567",
            store=None,
            is_active=True
    ):
        if store is None:
            store = create_store()
        return Manager.objects.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone=phone,
            store=store,
            is_active=is_active
        )

    return make_manager


@pytest.fixture
def create_customer():
    """Создание покупателя"""

    def make_customer(
            username="testcustomer",
            first_name="Петр",
            last_name="Петров",
            middle_name="Петрович",
            email="test@example.com",
            phone="+79998765432"
    ):
        return Customer.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            email=email,
            phone=phone
        )

    return make_customer


@pytest.fixture
def create_user():
    """Создание пользователя системы"""
    UserModel = get_user_model()

    def make_user(
            username="testuser",
            password="testpass123",
            first_name="Тест",
            last_name="Тестов",
            role=User.Role.CUSTOMER,
            manager_profile=None,
            customer_profile=None
    ):
        user = UserModel.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        if manager_profile:
            user.manager_profile = manager_profile
        if customer_profile:
            user.customer_profile = customer_profile
        user.save()
        return user

    return make_user


@pytest.fixture
def create_product(create_category, create_store, create_manager):
    """Создание товара"""

    def make_product(
            name="Телефон",
            price=999.99,
            available=True,
            category=None,
            store=None,
            created_by=None,
            with_image=False
    ):
        if category is None:
            category = create_category()
        if store is None:
            store = create_store()
        if created_by is None:
            created_by = create_manager()

        image = None
        if with_image:
            image = SimpleUploadedFile(
                "test_image.jpg",
                b"file_content",
                content_type="image/jpeg"
            )

        return Product.objects.create(
            name=name,
            price=price,
            available=available,
            category=category,
            store=store,
            created_by=created_by,
            image=image
        )

    return make_product


@pytest.fixture
def create_favorite_product(create_customer, create_product):
    """Создание избранного товара"""

    def make_favorite(user=None, product=None):
        if user is None:
            user = create_customer()
        if product is None:
            product = create_product()
        return FavoriteProduct.objects.create(user=user, product=product)

    return make_favorite


@pytest.fixture
def create_cart_item(create_customer, create_product):
    """Создание элемента корзины"""

    def make_cart_item(user=None, product=None, quantity=1):
        if user is None:
            user = create_customer()
        if product is None:
            product = create_product()
        return CartItem.objects.create(
            user=user,
            product=product,
            quantity=quantity
        )

    return make_cart_item


@pytest.fixture
def create_order(create_customer, create_manager):
    """Создание заказа"""

    def make_order(
            user=None,
            salesman=None,
            total_price=1000.00,
            status="pending"
    ):
        if user is None:
            user = create_customer()
        if salesman is None:
            salesman = create_manager()
        return Order.objects.create(
            user=user,
            salesman=salesman,
            total_price=total_price,
            status=status
        )

    return make_order


@pytest.fixture
def create_order_item(create_order, create_product):
    """Создание элемента заказа"""

    def make_order_item(order=None, product=None, quantity=2, price_at_order=500.00):
        if order is None:
            order = create_order()
        if product is None:
            product = create_product()
        return OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_order=price_at_order
        )

    return make_order_item


@pytest.fixture
def create_action_log(create_user, create_product):
    """Создание лога действий"""

    def make_action_log(
            user=None,
            action_type="CREATE",
            product_name="Тестовый товар",
            product_id=None,
            changed_fields=None
    ):
        if user is None:
            user = create_user()
        if changed_fields is None:
            changed_fields = {"price": 1000.00}

        return ActionLog.objects.create(
            user=user,
            action_type=action_type,
            product_name=product_name,
            product_id=product_id,
            changed_fields=changed_fields
        )

    return make_action_log


@pytest.fixture
def authenticated_client(client, create_user):
    """Аутентифицированный клиент"""

    def make_client(role=User.Role.CUSTOMER, **user_kwargs):
        user = create_user(role=role, **user_kwargs)
        client.force_login(user)
        return client

    return make_client


@pytest.fixture
def customer_client(authenticated_client):
    """Клиент с правами покупателя"""
    return authenticated_client(role=User.Role.CUSTOMER)


@pytest.fixture
def manager_client(authenticated_client):
    """Клиент с правами менеджера"""
    return authenticated_client(role=User.Role.MANAGER)


@pytest.fixture
def admin_client(authenticated_client):
    """Клиент с правами администратора"""
    return authenticated_client(role=User.Role.ADMIN)


@pytest.fixture
def user_data():
    """Данные для регистрации пользователя"""
    return {
        'username': 'newuser',
        'password1': 'complexpass123',
        'password2': 'complexpass123',
        'first_name': 'Новый',
        'last_name': 'Пользователь',
        'email': 'new@example.com'
    }


@pytest.fixture
def login_data():
    """Данные для входа пользователя"""
    return {
        'username': 'testuser',
        'password': 'testpass123'
    }
