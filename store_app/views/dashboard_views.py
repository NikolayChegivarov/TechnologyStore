# Отображение
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from store_app.models import Product, Store, Category, FavoriteProduct
from django.db.models import Count
import random


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


def home(request):
    # Получаем все уникальные города
    cities = Store.objects.values_list('city', flat=True).distinct().order_by('city')

    # Получаем все категории, отсортированные по имени
    categories = Category.objects.all().order_by('name')

    # Получаем все филиалы, отсортированные по городу и адресу
    stores = Store.objects.all().order_by('city', 'address')

    # Начальный запрос для доступных товаров
    products = Product.objects.filter(available=True).select_related('category', 'store')

    # Получаем параметры фильтрации из GET-запроса
    selected_city = request.GET.get('city')
    selected_store = request.GET.get('store')
    selected_category = request.GET.get('category')

    # Применяем фильтры
    if selected_city:
        products = products.filter(store__city=selected_city)
        stores = stores.filter(city=selected_city)

    if selected_store:
        products = products.filter(store_id=selected_store)

    if selected_category:
        products = products.filter(category_id=selected_category)

    # Если нет фильтров, показываем случайные 12 товаров
    if not any([selected_city, selected_store, selected_category]):
        product_count = products.count()
        if product_count > 12:
            product_ids = list(products.values_list('id', flat=True))
            random_ids = random.sample(product_ids, 12)
            products = products.filter(id__in=random_ids)
        else:
            products = products.order_by('?')[:12]

    # Получаем список избранных товаров для авторизованного пользователя
    user_favorites = []
    if request.user.is_authenticated and request.user.role == 'CUSTOMER' and hasattr(request.user, 'customer_profile'):
        user_favorites = FavoriteProduct.objects.filter(
            user=request.user.customer_profile
        ).values_list('product_id', flat=True)

    context = {
        'products': products,
        'cities': cities,
        'stores': stores,
        'categories': categories,
        'selected_city': selected_city,
        'selected_store': selected_store,
        'selected_category': selected_category,
        'user_favorites': list(user_favorites),
    }

    return render(request, 'home.html', context)


def get_stores_by_city(request):
    city = request.GET.get('city')
    stores = Store.objects.filter(city=city).values('id', 'address')
    return JsonResponse({'stores': list(stores)})


