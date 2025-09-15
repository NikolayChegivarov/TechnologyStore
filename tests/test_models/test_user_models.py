# pytest tests/test_models/test_user_models.py -v
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from store_app.models import User, Manager, Customer, Store


@pytest.mark.django_db
class TestUserModel:
    """Тесты для модели User"""

    def test_create_user_with_valid_data(self):
        """Тест создания пользователя с валидными данными"""
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="Иван",
            last_name="Петров",
            role=User.Role.CUSTOMER
        )

        assert user.username == "testuser"
        assert user.check_password("testpass123")
        assert user.first_name == "Иван"
        assert user.last_name == "Петров"
        assert user.role == User.Role.CUSTOMER
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        superuser = User.objects.create_superuser(
            username="admin",
            password="adminpass123",
            first_name="Админ",
            last_name="Системный"
        )

        assert superuser.username == "admin"
        assert superuser.check_password("adminpass123")
        assert superuser.is_staff is True
        assert superuser.is_superuser is True

    def test_user_str_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="Иван",
            last_name="Петров"
        )

        assert str(user) == "testuser"
        assert user.get_full_name() == "Иван Петров"
        assert user.get_short_name() == "Иван"

    def test_user_role_choices(self):
        """Тест доступных ролей пользователя"""
        assert User.Role.ADMIN == 'ADMIN'
        assert User.Role.MANAGER == 'MANAGER'
        assert User.Role.CUSTOMER == 'CUSTOMER'
        assert len(User.Role.choices) == 3

    def test_user_username_validation(self):
        """Тест валидации имени пользователя"""
        # Валидные символы
        user = User.objects.create_user(
            username="user123@test.ru",
            password="testpass123",
            first_name="Тест",
            last_name="Тестов"
        )
        assert user is not None

        # Невалидные символы
        with pytest.raises(ValidationError):
            user = User(username="user#invalid")
            user.full_clean()

    def test_user_name_cyrillic_validation(self):
        """Тест валидации кириллических имен"""
        # Валидные кириллические имена
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="Иван",
            last_name="Петров"
        )
        assert user is not None

        # Невалидные символы в имени
        with pytest.raises(ValidationError):
            user = User(
                username="testuser2",
                first_name="John",  # Латинские буквы
                last_name="Doe"
            )
            user.full_clean()

    def test_user_password_hashing(self):
        """Тест хеширования пароля при сохранении"""
        user = User.objects.create_user(
            username="testuser",
            password="plainpassword",
            first_name="Тест",
            last_name="Тестов"
        )

        assert user.password.startswith('pbkdf2_sha256$')
        assert user.check_password("plainpassword")
        assert not user.check_password("wrongpassword")

    def test_unique_username_constraint(self):
        """Тест уникальности имени пользователя"""
        User.objects.create_user(
            username="uniqueuser",
            password="testpass123",
            first_name="Тест",
            last_name="Тестов"
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="uniqueuser",  # Дубликат
                password="testpass123",
                first_name="Другой",
                last_name="Пользователь"
            )


@pytest.mark.django_db
class TestManagerModel:
    """Тесты для модели Manager"""

    def test_create_manager(self, test_store):
        """Тест создания менеджера"""
        manager = Manager.objects.create(
            store=test_store,
            last_name="Сидоров",
            first_name="Алексей",
            middle_name="Викторович",
            phone="+7 999 111 22 33",
            position="Старший менеджер"
        )

        assert manager.last_name == "Сидоров"
        assert manager.first_name == "Алексей"
        assert manager.middle_name == "Викторович"
        assert manager.phone == "+7 999 111 22 33"
        assert manager.position == "Старший менеджер"
        assert manager.store == test_store
        assert manager.is_active is True

    def test_manager_str_representation(self, test_store):
        """Тест строкового представления менеджера"""
        manager = Manager.objects.create(
            store=test_store,
            last_name="Сидоров",
            first_name="Алексей",
            middle_name="Викторович",
            phone="+7 999 111 22 33"
        )

        assert str(manager) == "Сидоров Алексей Викторович"
        assert manager.get_full_name() == "Сидоров Алексей Викторович"

    def test_manager_name_validation(self, test_store):
        """Тест валидации имени менеджера"""
        # Валидные кириллические имена
        manager = Manager(
            store=test_store,
            last_name="Иванов",
            first_name="Петр",
            middle_name="Сергеевич",
            phone="+7 999 123 45 67"
        )
        manager.full_clean()  # Не должно вызывать исключение

        # Невалидные символы в имени
        with pytest.raises(ValidationError):
            manager = Manager(
                store=test_store,
                last_name="Smith",  # Латинские буквы
                first_name="John",
                phone="+7 999 123 45 67"
            )
            manager.full_clean()

    def test_manager_phone_validation(self, test_store):
        """Тест валидации телефона менеджера"""
        # Валидный телефон
        manager = Manager(
            store=test_store,
            last_name="Иванов",
            first_name="Петр",
            phone="+79991234567"  # Без пробелов
        )
        manager.full_clean()

        # Невалидный телефон
        with pytest.raises(ValidationError):
            manager = Manager(
                store=test_store,
                last_name="Иванов",
                first_name="Петр",
                phone="abc123"  # Не цифры
            )
            manager.full_clean()


@pytest.mark.django_db
class TestCustomerModel:
    """Тесты для модели Customer"""

    def test_create_customer(self):
        """Тест создания покупателя"""
        customer = Customer.objects.create(
            username="testcustomer",
            last_name="Петров",
            first_name="Иван",
            middle_name="Васильевич",
            email="ivan@example.com",
            phone="+7 999 888 77 66",
            address="ул. Примерная, д. 5"
        )

        assert customer.username == "testcustomer"
        assert customer.last_name == "Петров"
        assert customer.first_name == "Иван"
        assert customer.middle_name == "Васильевич"
        assert customer.email == "ivan@example.com"
        assert customer.phone == "+7 999 888 77 66"
        assert customer.address == "ул. Примерная, д. 5"

    def test_customer_str_representation(self):
        """Тест строкового представления покупателя"""
        customer = Customer.objects.create(
            username="testcustomer",
            last_name="Петров",
            first_name="Иван",
            email="ivan@example.com",
            phone="+7 999 888 77 66"
        )

        assert str(customer) == "Петров Иван"
        assert customer.get_full_name() == "Петров Иван"

    def test_customer_unique_username(self):
        """Тест уникальности имени пользователя покупателя"""
        Customer.objects.create(
            username="unique_customer",
            last_name="Петров",
            first_name="Иван",
            phone="+7 999 888 77 66"
        )

        with pytest.raises(IntegrityError):
            Customer.objects.create(
                username="unique_customer",  # Дубликат
                last_name="Сидоров",
                first_name="Алексей",
                phone="+7 999 111 22 33"
            )

    def test_customer_address_validation(self):
        """Тест валидации адреса покупателя"""
        # Валидный адрес
        customer = Customer(
            username="testcustomer",
            last_name="Петров",
            first_name="Иван",
            phone="+7 999 888 77 66",
            email="test@example.com",  # Добавить обязательное поле email
            address="ул. Московская, д. 15, кв. 42"  # Кириллица, цифры, знаки
        )
        customer.full_clean()

        # Невалидный адрес
        with pytest.raises(ValidationError):
            customer = Customer(
                username="testcustomer2",
                last_name="Петров",
                first_name="Иван",
                phone="+7 999 888 77 66",
                email="test2@example.com",  # Добавить email
                address="Street 15, apt 42"  # Латинские буквы
            )
            customer.full_clean()


@pytest.mark.django_db
class TestUserProfileRelationships:
    """Тесты связей между User, Manager и Customer"""

    def test_manager_user_relationship(self, test_manager_with_user):
        """Тест связи пользователя с профилем менеджера"""
        user, manager = test_manager_with_user
        assert user.manager_profile == manager
        assert manager.user_account == user
        assert user.role == User.Role.MANAGER

    def test_customer_user_relationship(self, test_customer_with_user):
        """Тест связи пользователя с профилем покупателя"""
        user, customer = test_customer_with_user
        assert user.customer_profile == customer
        assert customer.user_account == user
        assert user.role == User.Role.CUSTOMER

    def test_manager_profile_sync_on_user_save(self, test_manager):
        """Тест синхронизации данных менеджера при сохранении пользователя"""
        user = User.objects.create_user(
            username="sync_test",
            password="testpass123",
            first_name="НовоеИмя",
            last_name="НоваяФамилия",
            role=User.Role.MANAGER,
            manager_profile=test_manager
        )

        # Данные должны синхронизироваться
        test_manager.refresh_from_db()
        assert test_manager.first_name == "НовоеИмя"
        assert test_manager.last_name == "НоваяФамилия"

    def test_user_deletion_cascades_to_profiles(self, test_customer_with_user):
        """Тест каскадного удаления профилей при удалении пользователя"""
        user, customer = test_customer_with_user
        customer_id = customer.id
        user_id = user.id

        user.delete()

        # Проверяем, что пользователь удален
        with pytest.raises(User.DoesNotExist):
            User.objects.get(id=user_id)

        # Проверяем, что профиль покупателя все еще существует
        customer = Customer.objects.get(id=customer_id)

        # Проверяем, что связь обнулилась (обращение к user_account вызывает исключение)
        with pytest.raises(Customer.user_account.RelatedObjectDoesNotExist):
            _ = customer.user_account  # Попытка доступа к связи


