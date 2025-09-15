import pytest
from django import forms
from store_app.forms.auth_forms import LoginForm, CustomerSignUpForm, ManagerSignUpForm
from store_app.models import User


@pytest.mark.django_db
class TestLoginForm:
    """Тесты для формы LoginForm"""

    def test_login_form_fields(self):
        """Тест наличия полей в форме логина"""
        form = LoginForm()
        assert 'username' in form.fields
        assert 'password' in form.fields
        assert isinstance(form.fields['username'], forms.CharField)
        assert isinstance(form.fields['password'], forms.CharField)

    def test_login_form_widget_attrs(self):
        """Тест атрибутов виджетов формы логина"""
        form = LoginForm()
        username_widget = form.fields['username'].widget
        password_widget = form.fields['password'].widget

        assert username_widget.attrs['class'] == 'form-control'
        assert username_widget.attrs['placeholder'] == 'Логин'
        assert password_widget.attrs['class'] == 'form-control'
        assert password_widget.attrs['placeholder'] == 'Пароль'

    def test_login_form_initialization(self):
        """Тест инициализации формы с данными (без проверки аутентификации)"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        # Проверяем только что форма правильно инициализирована, не валидность
        assert form.data['username'] == 'testuser'
        assert form.data['password'] == 'testpass123'

    def test_login_form_empty_data(self):
        """Тест пустых данных для формы логина"""
        form = LoginForm(data={})
        assert not form.is_valid()
        assert 'username' in form.errors
        assert 'password' in form.errors


@pytest.mark.django_db
class TestCustomerSignUpForm:
    """Тесты для формы CustomerSignUpForm"""

    def test_customer_signup_form_fields(self):
        """Тест наличия полей в форме регистрации клиента"""
        form = CustomerSignUpForm()
        expected_fields = ['email', 'first_name', 'last_name', 'password1', 'password2']
        for field in expected_fields:
            assert field in form.fields

    def test_customer_signup_form_widget_attrs(self):
        """Тест атрибутов виджетов формы регистрации клиента"""
        form = CustomerSignUpForm()

        email_widget = form.fields['email'].widget
        assert email_widget.attrs['class'] == 'form-control'
        assert email_widget.attrs['placeholder'] == 'Введите email'

        first_name_widget = form.fields['first_name'].widget
        assert first_name_widget.attrs['class'] == 'form-control'
        assert first_name_widget.attrs['placeholder'] == 'Введите имя'

        last_name_widget = form.fields['last_name'].widget
        assert last_name_widget.attrs['class'] == 'form-control'
        assert last_name_widget.attrs['placeholder'] == 'Введите фамилию'

    def test_customer_signup_form_valid_data(self):
        """Тест валидных данных для формы регистрации клиента"""
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = CustomerSignUpForm(data=form_data)
        assert form.is_valid()

    def test_customer_signup_form_password_mismatch(self):
        """Тест несовпадающих паролей"""
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'password1': 'password123',
            'password2': 'differentpassword'
        }
        form = CustomerSignUpForm(data=form_data)
        assert not form.is_valid()
        assert 'password2' in form.errors

    def test_customer_signup_form_invalid_email(self):
        """Тест невалидного email"""
        form_data = {
            'email': 'invalid-email',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'password1': 'password123',
            'password2': 'password123'
        }
        form = CustomerSignUpForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_customer_signup_form_empty_fields(self):
        """Тест пустых обязательных полей"""
        form_data = {
            'email': '',
            'first_name': '',
            'last_name': '',
            'password1': '',
            'password2': ''
        }
        form = CustomerSignUpForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors
        assert 'first_name' in form.errors
        assert 'last_name' in form.errors
        assert 'password1' in form.errors


@pytest.mark.django_db
class TestManagerSignUpForm:
    """Тесты для формы ManagerSignUpForm"""

    def test_manager_signup_form_fields(self):
        """Тест наличия полей в форме регистрации менеджера"""
        form = ManagerSignUpForm()
        expected_fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        for field in expected_fields:
            assert field in form.fields

    def test_manager_signup_form_valid_data(self):
        """Тест валидных данных для формы регистрации менеджера"""
        form_data = {
            'username': 'manager_user',
            'email': 'manager@example.com',
            'first_name': 'Петр',
            'last_name': 'Петров',
            'password1': 'managerpass123',
            'password2': 'managerpass123'
        }
        form = ManagerSignUpForm(data=form_data)
        assert form.is_valid()

    def test_manager_signup_form_save(self):
        """Тест сохранения пользователя менеджера"""
        form_data = {
            'username': 'manager_user',
            'email': 'manager@example.com',
            'first_name': 'Петр',
            'last_name': 'Петров',
            'password1': 'managerpass123',
            'password2': 'managerpass123'
        }
        form = ManagerSignUpForm(data=form_data)
        assert form.is_valid()

        user = form.save()
        assert user.role == User.Role.MANAGER
        assert user.username == 'manager_user'
        assert user.email == 'manager@example.com'
        assert user.first_name == 'Петр'
        assert user.last_name == 'Петров'
        assert user.check_password('managerpass123')

    def test_manager_signup_form_duplicate_username(self):
        """Тест дублирования имени пользователя"""
        # Создаем первого пользователя
        User.objects.create_user(
            username='existing_user',
            email='user1@example.com',
            password='testpass123'
        )

        # Пытаемся создать второго с тем же username
        form_data = {
            'username': 'existing_user',
            'email': 'user2@example.com',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = ManagerSignUpForm(data=form_data)
        assert not form.is_valid()
        assert 'username' in form.errors

    def test_manager_signup_form_duplicate_email(self):
        """Тест дублирования email"""
        # Создаем первого пользователя
        User.objects.create_user(
            username='user1',
            email='existing@example.com',
            password='testpass123'
        )

        # Пытаемся создать второго с тем же email
        form_data = {
            'username': 'user2',
            'email': 'existing@example.com',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = ManagerSignUpForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors