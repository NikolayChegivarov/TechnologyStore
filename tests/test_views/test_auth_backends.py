import pytest
from store_app.auth_backends import RoleBasedAuthBackend
from store_app.models import User


@pytest.mark.django_db
class TestRoleBasedAuthBackend:
    """Тесты для RoleBasedAuthBackend - кастомной аутентификации по ролям"""

    def test_authenticate_manager_by_username(self, test_manager_with_user):
        """Тест использует фактическое имя пользователя из фикстуры"""
        user, manager = test_manager_with_user
        backend = RoleBasedAuthBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='test_manager',  # Используем реальное имя из фикстуры
            password='testpass123'
        )
        assert authenticated_user == user

    def test_authenticate_admin_by_username(self, test_admin_user):
        """Тест аутентификации администратора по имени пользователя"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='admin_user',  # Используем имя из фикстуры test_admin_user
            password='testpass123'
        )
        assert user == test_admin_user

    def test_authenticate_customer_by_email(self, test_customer_with_user):
        """Тест аутентификации клиента по email"""
        user, customer = test_customer_with_user
        backend = RoleBasedAuthBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='customer@example.com',  # Используем email из фикстуры test_customer_with_user
            password='testpass123'
        )
        assert authenticated_user == user

    def test_authenticate_manager_wrong_password(self, test_manager_with_user):
        """Тест неудачной аутентификации менеджера с неверным паролем"""
        user, manager = test_manager_with_user
        backend = RoleBasedAuthBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='test_manager',
            password='wrongpass'
        )
        assert authenticated_user is None

    def test_authenticate_customer_wrong_password(self, test_customer_with_user):
        """Тест неудачной аутентификации клиента с неверным паролем"""
        user, customer = test_customer_with_user
        backend = RoleBasedAuthBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='customer@example.com',
            password='wrongpass'
        )
        assert authenticated_user is None

    def test_authenticate_none_username(self):
        """Тест аутентификации с пустым именем пользователя"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username=None,
            password='testpass123'
        )
        assert user is None

    def test_authenticate_none_password(self, test_manager_with_user):
        """Тест аутентификации с пустым паролем"""
        user, manager = test_manager_with_user
        backend = RoleBasedAuthBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='test_manager',  # Используем имя из фикстуры test_manager_with_user
            password=None  # Пустой пароль
        )
        assert authenticated_user is None

    def test_authenticate_customer_by_username_fails(self, test_customer_with_user):
        """Тест неудачной аутентификации клиента по имени пользователя"""
        user, customer = test_customer_with_user
        backend = RoleBasedAuthBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='customer_user',  # Несуществующее имя пользователя
            password='testpass123'
        )
        assert authenticated_user is None

    def test_authenticate_manager_by_email_fails(self, test_manager_with_user):
        """Тест неудачной аутентификации менеджера по email"""
        user, manager = test_manager_with_user
        backend = RoleBasedAuthBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='manager@test.com',  # Несуществующий email
            password='testpass123'
        )
        assert authenticated_user is None

    def test_authenticate_nonexistent_user(self):
        """Тест аутентификации несуществующего пользователя"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='nonexistent',
            password='testpass123'
        )
        assert user is None
