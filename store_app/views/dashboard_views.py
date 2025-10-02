# дашборд вью
# Отображение
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from store_app.models import Product, Store, Category, FavoriteProduct
from django.contrib import messages
from django.db.models import Count
import random


@login_required
def manager_dashboard(request):
    """Отображает панель управления менеджера с сортировкой товаров:
    - Доступные товары (available=True) показываются первыми
    - Недоступные товары (available=False) сортируются по дате обновления (updated_at)
    - Самые "старые" недоступные товары показываются внизу списка
    """
    # Получаем параметры фильтрации из GET-запроса
    selected_store = request.GET.get('store')
    selected_category = request.GET.get('category')

    # Получаем все товары с правильной сортировкой
    products = Product.objects.all().order_by(
        '-available',  # Сначала доступные (True), потом недоступные (False)
        '-updated_at' if request.GET.get('sort') == 'newest' else 'updated_at'
    )

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
    print("=== HOME VIEW CALLED ===")
    print("GET параметры:", dict(request.GET))
    print("AJAX запрос:", request.headers.get('X-Requested-With'))

    # Получаем все уникальные города
    cities = Store.objects.values_list('city', flat=True).distinct().order_by('city')
    categories = Category.objects.all().order_by('name')
    stores = Store.objects.all().order_by('city', 'address')

    # Базовый запрос
    products = Product.objects.filter(available=True).select_related('category', 'store')

    # Параметры
    selected_city = request.GET.get('city')
    selected_store = request.GET.get('store')
    selected_category = request.GET.get('category')
    page = int(request.GET.get('page', 1))

    # Применяем фильтры
    if selected_city:
        products = products.filter(store__city=selected_city)
    if selected_store:
        products = products.filter(store_id=selected_store)
    if selected_category:
        products = products.filter(category_id=selected_category)

    products_per_page = 12
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    print(f"Всего товаров после фильтров: {products.count()}")
    print(f"Страница: {page}, AJAX: {is_ajax}")

    # AJAX запрос для подгрузки
    if is_ajax and page > 1:
        print("Обрабатываем AJAX запрос")
        start_index = (page - 1) * products_per_page
        end_index = start_index + products_per_page
        paginated_products = list(products[start_index:end_index])

        print(f"Загружаем товары с {start_index} по {end_index}: {len(paginated_products)} шт.")

        user_favorites = []
        if request.user.is_authenticated and request.user.role == 'CUSTOMER' and hasattr(request.user,
                                                                                         'customer_profile'):
            user_favorites = FavoriteProduct.objects.filter(
                user=request.user.customer_profile
            ).values_list('product_id', flat=True)

        context = {
            'products': paginated_products,
            'user_favorites': list(user_favorites),
        }

        return render(request, 'home_products_partial.html', context)

    # Первая загрузка страницы
    initial_products = products[:products_per_page]
    print(f"Первоначальная загрузка: {len(initial_products)} товаров")

    user_favorites = []
    if request.user.is_authenticated and request.user.role == 'CUSTOMER' and hasattr(request.user, 'customer_profile'):
        user_favorites = FavoriteProduct.objects.filter(
            user=request.user.customer_profile
        ).values_list('product_id', flat=True)

    context = {
        'products': initial_products,
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


def customer_profile(request):
    """
    Представление для отображения личного кабинета покупателя
    """
    # Проверяем, что пользователь действительно покупатель
    if request.user.role != 'CUSTOMER':
        messages.error(request, 'Доступ только для покупателей')
        return redirect('home')

    # Получаем количество избранных товаров
    favorite_count = 0
    if hasattr(request.user, 'customer_profile'):
        favorite_count = FavoriteProduct.objects.filter(
            user=request.user.customer_profile
        ).count()

    context = {
        'user': request.user,
        'favorite_count': favorite_count,
    }

    return render(request, 'dashboard/customer.html', context)

def ContactsView(request):
    """Контакты"""
    return render(request, 'basement/сontacts.html')


