import pytest
from store_app.auth_backends import RoleBasedAuthBackend
from store_app.models import User


@pytest.mark.django_db
class TestRoleBasedAuthBackend:
    """Тесты для RoleBasedAuthBackend - кастомной аутентификации по ролям"""

    def test_authenticate_manager_by_username(self, manager_user):
        """Тест аутентификации менеджера по имени пользователя"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='manager_user',
            password='testpass123'
        )
        assert user == manager_user

    def test_authenticate_admin_by_username(self, admin_user):
        """Тест аутентификации администратора по имени пользователя"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='admin_user',
            password='testpass123'
        )
        assert user == admin_user

    def test_authenticate_customer_by_email(self, customer_user):
        """Тест аутентификации клиента по email"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='customer@test.com',
            password='testpass123'
        )
        assert user == customer_user

    def test_authenticate_manager_wrong_password(self, manager_user):
        """Тест неудачной аутентификации менеджера с неверным паролем"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='manager_user',
            password='wrongpass'
        )
        assert user is None

    def test_authenticate_customer_wrong_password(self, customer_user):
        """Тест неудачной аутентификации клиента с неверным паролем"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='customer@test.com',
            password='wrongpass'
        )
        assert user is None

    def test_authenticate_none_username(self):
        """Тест аутентификации с пустым именем пользователя"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username=None,
            password='testpass123'
        )
        assert user is None

    def test_authenticate_none_password(self, manager_user):
        """Тест аутентификации с пустым паролем"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='manager_user',
            password=None
        )
        assert user is None

    def test_authenticate_customer_by_username_fails(self, customer_user):
        """Тест неудачной аутентификации клиента по имени пользователя"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='customer_user',
            password='testpass123'
        )
        assert user is None

    def test_authenticate_manager_by_email_fails(self, manager_user):
        """Тест неудачной аутентификации менеджера по email"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='manager@test.com',
            password='testpass123'
        )
        assert user is None

    def test_authenticate_nonexistent_user(self):
        """Тест аутентификации несуществующего пользователя"""
        backend = RoleBasedAuthBackend()
        user = backend.authenticate(
            request=None,
            username='nonexistent',
            password='testpass123'
        )
        assert user is None
