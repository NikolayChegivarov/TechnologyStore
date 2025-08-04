# Отображение
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from store_app.models import Product, Store, Category


@login_required
def customer_dashboard(request):
    """Отображает личный кабинет клиента:
    - Доступен только для авторизованных пользователей
    - Показывает интерфейс и функционал для клиентов
    - Использует шаблон dashboard/customer.html"""
    return render(request, 'dashboard/customer.html')

# @login_required
# def manager_dashboard(request):
#     return render(request, 'dashboard/manager.html')

@login_required
def manager_dashboard(request):
    """Отображает панель управления менеджера:
    - Доступен только для авторизованных менеджеров
    - Содержит инструменты управления для менеджеров
    - Использует шаблон dashboard/manager.html"""
    # Получаем параметры фильтрации из GET-запроса
    selected_store = request.GET.get('store')
    selected_category = request.GET.get('category')

    # Получаем все товары
    products = Product.objects.all()

    # Применяем фильтры
    if selected_store:
        products = products.filter(store_id=selected_store)
    if selected_category:
        products = products.filter(category_id=selected_category)

    # Получаем все филиалы и категории для выпадающих списков
    stores = Store.objects.all()
    categories = Category.objects.all()

    context = {
        'products': products,
        'stores': stores,
        'categories': categories,
        'selected_store': selected_store,
        'selected_category': selected_category,
    }
    return render(request, 'dashboard/manager.html', context)


