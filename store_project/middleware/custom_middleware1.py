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
        """
        Обрабатывает входящий HTTP-запрос до вызова представления.

        - Если пользователь неавторизован и пытается получить доступ к закрытой странице (не home, login или signup),
          происходит перенаправление на страницу входа.
        - Для авторизованных пользователей проверяется соответствие между URL и их ролью:
            * Менеджер может заходить только на /manager/*
            * Покупатель — только на /customer/*
        - Суперпользователю разрешён доступ ко всем страницам.

        Возвращает None (разрешение на выполнение представления) или редирект/ошибку 403.
        """
        # Пропускаем медиа-файлы и статику и админку
        if request.path.startswith(('/media/', '/static/', '/admin/')):
            return None

        if not request.user.is_authenticated:
            # Разрешаем доступ к публичным страницам
            public_paths = [
                '/',  # home
                '/login/',
                '/signup/',
                '/customer/signup/',
                '/manager/signup/',
                '/privacy/',
                'home/contacts/',
            ]

            # Разрешаем доступ к URL деталей товара и контактов (по началу пути)
            if (request.path.startswith('/product/') or
                    request.path.startswith('home/contacts/') or
                    any(request.path == path or request.path.startswith(path) for path in public_paths)):
                return None

            # Для всех остальных страниц - редирект на логин
            return redirect('login')

        # Для суперпользователя разрешаем доступ ко всему
        if request.user.is_superuser:
            return None

        # Проверяем доступ к страницам в зависимости от роли
        if request.path.startswith('/manager/') and request.user.role != User.Role.MANAGER:
            return HttpResponseForbidden()

        if request.path.startswith('/customer/') and request.user.role != User.Role.CUSTOMER:
            return HttpResponseForbidden()

        return None
