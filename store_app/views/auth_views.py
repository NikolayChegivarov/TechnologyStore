# Регистрация клиента, менеджера / авторизация.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import CreateView
from ..forms.auth_forms import LoginForm, CustomerSignUpForm, ManagerSignUpForm
from ..models import User, Customer
from django.contrib import messages
from uuid import uuid4


class CustomerSignUpView(CreateView):
    """Обрабатывает регистрацию нового клиента:
    - Отображает форму регистрации
    - Создает нового пользователя с ролью клиента
    - Автоматически авторизует пользователя после успешной регистрации
    - Перенаправляет на домашнюю страницу"""
    form_class = CustomerSignUpForm
    template_name = 'auth/signup.html'

    def form_valid(self, form):
        # Сохраняем объект User, но пока не коммитим
        user = form.save(commit=False)
        user.role = User.Role.CUSTOMER

        # Создаём Customer-профиль
        customer = Customer.objects.create(
            username=f"user_{uuid4().hex[:8]}",  # временный логин, если username больше не нужен — уберите
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone="",  # можно заменить на form.cleaned_data.get("phone") если есть
        )

        # Привязываем профиль
        user.customer_profile = customer
        user.save()

        # Логиним и перенаправляем
        login(self.request, user)
        return redirect('home')  # name='home' — как указано в urlpatterns


class ManagerSignUpView(CreateView):
    """Обрабатывает регистрацию нового менеджера:
    - Отображает форму регистрации для менеджеров
    - Создает нового пользователя с ролью менеджера
    - Автоматически выполняет вход после успешной регистрации
    - Перенаправляет на dashboard менеджера"""
    form_class = ManagerSignUpForm
    template_name = 'auth/signup.html'
    success_url = '/manager/dashboard/'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


def login_view(request):
    """Обрабатывает вход пользователя и перенаправляет его в зависимости от роли."""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin:index')
        elif request.user.role == User.Role.MANAGER:
            return redirect('manager_dashboard')
        elif request.user.role == User.Role.CUSTOMER:
            return redirect('customer_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('admin:index')
            elif user.role == User.Role.MANAGER:
                return redirect('manager_dashboard')
            elif user.role == User.Role.CUSTOMER:
                return redirect('customer_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})