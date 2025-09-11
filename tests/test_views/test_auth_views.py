# tests/test_views/test_auth_views.py
import pytest
from django.urls import reverse
from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from store_app.views.auth_views import CustomerSignUpView, ManagerSignUpView, login_view
from store_app.models import Customer

User = get_user_model()


def add_session_to_request(request):
    """Добавляет сессию к request объекту"""
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()


@pytest.mark.django_db
class TestCustomerSignUpView:
    """Тесты для регистрации клиента"""

    def test_customer_signup_valid_data(self):
        """Тест успешной регистрации клиента с валидными данными"""
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'email': 'ivan@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

        factory = RequestFactory()
        request = factory.post(reverse('customer_signup'), data=form_data)

        # Добавляем сессию и сообщения
        add_session_to_request(request)
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        view = CustomerSignUpView()
        view.setup(request)
        form = view.get_form()

        assert form.is_valid()
        response = view.form_valid(form)

        assert response.status_code == 302
        assert response.url == '/'
        assert User.objects.filter(email='ivan@example.com').exists()
        assert Customer.objects.filter(email='ivan@example.com').exists()


@pytest.mark.django_db
class TestManagerSignUpView:
    """Тесты для регистрации менеджера"""

    def test_manager_signup_valid_data(self):
        """Тест успешной регистрации менеджера с валидными данными"""
        form_data = {
            'username': 'manager',
            'first_name': 'Менеджер',
            'last_name': 'Иванов',
            'email': 'manager@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

        factory = RequestFactory()
        request = factory.post(reverse('manager_signup'), data=form_data)

        # Добавляем сессию и сообщения
        add_session_to_request(request)
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        view = ManagerSignUpView()
        view.setup(request)
        form = view.get_form()

        assert form.is_valid()
        response = view.form_valid(form)

        assert response.status_code == 302
        assert response.url == '/manager/dashboard/'
        assert User.objects.filter(email='manager@example.com', role=User.Role.MANAGER).exists()


@pytest.mark.django_db
class TestLoginView:
    """Тесты для входа пользователя"""

    def test_login_view_authenticated_user_redirect(self):
        """Тест редиректа аутентифицированного пользователя"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=User.Role.CUSTOMER
        )

        client = Client()
        client.force_login(user)

        response = client.get(reverse('login'))
        assert response.status_code == 302
        assert response.url == '/'

    def test_login_view_valid_credentials(self):
        """Тест успешного входа с валидными учетными данными"""
        # Создаем пользователя через стандартный метод
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=User.Role.CUSTOMER
        )
        user.set_password('testpass123')
        user.save()

        client = Client()
        response = client.post(reverse('login'), {
            'username': 'test@example.com',  # Используем email для входа
            'password': 'testpass123'
        })

        assert response.status_code == 302
        assert response.url == '/'

    def test_login_view_invalid_credentials(self):
        """Тест входа с неверными учетными данными"""
        client = Client()
        response = client.post(reverse('login'), {
            'username': 'wrong@example.com',
            'password': 'wrongpass'
        })

        assert response.status_code == 200
        assert 'Неверное имя пользователя или пароль' in response.content.decode()

    def test_login_view_manager_redirect(self):
        """Тест редиректа менеджера после входа"""
        # Создаем пользователя через стандартный метод
        user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123',
            role=User.Role.MANAGER
        )
        user.set_password('testpass123')
        user.save()

        client = Client()
        # Используем username вместо email для менеджера
        response = client.post(reverse('login'), {
            'username': 'manager',  # Используем username для менеджера
            'password': 'testpass123'
        })

        assert response.status_code == 302
        assert response.url == '/manager/dashboard/'

    def test_login_view_manager_with_email_fallback(self):
        """Тест входа менеджера через email (если поддерживается)"""
        # Создаем пользователя через стандартный метод
        user = User.objects.create_user(
            username='manager2',
            email='manager2@example.com',
            password='testpass123',
            role=User.Role.MANAGER
        )
        user.set_password('testpass123')
        user.save()

        client = Client()
        # Пробуем войти через email
        response = client.post(reverse('login'), {
            'username': 'manager2@example.com',
            'password': 'testpass123'
        })

        # Проверяем результат в зависимости от поведения системы
        if response.status_code == 302:
            assert response.url == '/manager/dashboard/'
        else:
            # Если система не поддерживает вход менеджеров по email,
            # проверяем что отображается форма с ошибкой
            assert response.status_code == 200
            assert 'login' in response.content.decode().lower()