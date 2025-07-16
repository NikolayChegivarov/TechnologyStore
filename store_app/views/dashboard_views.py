# Отображение
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def customer_dashboard(request):
    """Отображает личный кабинет клиента:
    - Доступен только для авторизованных пользователей
    - Показывает интерфейс и функционал для клиентов
    - Использует шаблон dashboard/customer.html"""
    return render(request, 'dashboard/customer.html')

@login_required
def manager_dashboard(request):
    """Отображает панель управления менеджера:
    - Доступен только для авторизованных менеджеров
    - Содержит инструменты управления для менеджеров
    - Использует шаблон dashboard/manager.html"""
    return render(request, 'dashboard/manager.html')