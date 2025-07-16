# Кастомный middleware для проверки прав доступа на основе ролей пользователя
# Автоматически перенаправляет пользователей на нужные страницы и блокирует неавторизованный доступ
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.shortcuts import redirect

from store_app.models import User


class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            if request.path not in [reverse('login'), reverse('customer_signup'), reverse('manager_signup')]:
                return redirect('login')
            return None

        # Для суперпользователя разрешаем доступ ко всему
        if request.user.is_superuser:
            return None

        # Проверяем доступ к страницам в зависимости от роли
        if request.path.startswith('/manager/') and request.user.role != User.Role.MANAGER:
            return HttpResponseForbidden()

        if request.path.startswith('/customer/') and request.user.role != User.Role.CUSTOMER:
            return HttpResponseForbidden()

        return None