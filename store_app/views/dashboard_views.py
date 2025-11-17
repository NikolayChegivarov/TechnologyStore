
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from store_app.models import Product, Store, Category, FavoriteProduct
from django.contrib import messages
from django.db.models import Count
import random


def home(request):
    """Главная страница с товарами"""
    return buy_page(request)


def buy_page(request):
    """Страница покупки техники - переносим сюда основную логику из home"""
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
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    search_query = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))

    # Применяем фильтры
    if selected_city:
        products = products.filter(store__city=selected_city)
        stores = stores.filter(city=selected_city)

    if selected_store:
        products = products.filter(store_id=selected_store)

    if selected_category:
        products = products.filter(category_id=selected_category)

    # Фильтрация по цене
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # Поиск по названию товара
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Количество товаров на страницу
    products_per_page = 12

    # Определяем, является ли это AJAX-запросом
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Если это AJAX-запрос для пагинации, возвращаем только товары
    if is_ajax and page > 1:
        start_index = (page - 1) * products_per_page
        end_index = start_index + products_per_page

        # Получаем товары для текущей страницы
        paginated_products = list(products[start_index:end_index])

        # Получаем список избранных товаров для авторизованного пользователя
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

    # Первоначальная загрузка страницы (не AJAX)
    initial_products = products[:products_per_page]

    # Получаем список избранных товаров для авторизованного пользователя
    user_favorites = []
    if request.user.is_authenticated and request.user.role == 'CUSTOMER' and hasattr(request.user, 'customer_profile'):
        user_favorites = FavoriteProduct.objects.filter(
            user=request.user.customer_profile
        ).values_list('product_id', flat=True)

    # Проверяем, применены ли фильтры
    filters_applied = any([
        selected_city, selected_store, selected_category,
        price_min, price_max, search_query
    ])

    context = {
        'products': initial_products,
        'cities': cities,
        'stores': stores,
        'categories': categories,
        'selected_city': selected_city,
        'selected_store': selected_store,
        'selected_category': selected_category,
        'selected_price_min': price_min,
        'selected_price_max': price_max,
        'selected_search': search_query,
        'user_favorites': list(user_favorites),
        'filters_applied': filters_applied,
    }

    return render(request, 'dashboard/home.html', context)


def sell_page(request):
    """Страница продажи техники"""
    return render(request, 'dashboard/sell.html')


@login_required
def manager_dashboard(request):
    """Отображает панель управления менеджера с сортировкой товаров:
    - Доступные товары (available=True) показываются первыми
    - Недоступные товары (available=False) сортируются по дате обновления (updated_at)
    - Самые "старые" недоступные товары показываются внизу списка
    """
    # Проверяем, что пользователь менеджер
    if request.user.role != 'MANAGER':
        messages.error(request, 'Доступ только для менеджеров')
        return redirect('home')

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


def get_stores_by_city(request):
    """AJAX-функция для получения филиалов по городу"""
    city = request.GET.get('city')
    stores = Store.objects.filter(city=city).values('id', 'address')
    return JsonResponse({'stores': list(stores)})


@login_required
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


@login_required
def favorites_view(request):
    """Страница избранных товаров"""
    if request.user.role != 'CUSTOMER':
        messages.error(request, 'Доступ только для покупателей')
        return redirect('home')

    if not hasattr(request.user, 'customer_profile'):
        messages.error(request, 'Профиль покупателя не найден')
        return redirect('home')

    # Получаем избранные товары пользователя
    favorite_products = FavoriteProduct.objects.filter(
        user=request.user.customer_profile
    ).select_related('product__category', 'product__store')

    products = [fp.product for fp in favorite_products]

    context = {
        'products': products,
        'favorite_count': len(products),
    }

    return render(request, 'favorites.html', context)


@login_required
def toggle_favorite(request):
    """Добавление/удаление товара из избранного"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)

    if request.user.role != 'CUSTOMER' or not hasattr(request.user, 'customer_profile'):
        return JsonResponse({'error': 'Доступ только для покупателей'}, status=403)

    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'error': 'ID товара не указан'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Товар не найден'}, status=404)

    customer_profile = request.user.customer_profile

    # Проверяем, есть ли уже товар в избранном
    favorite, created = FavoriteProduct.objects.get_or_create(
        user=customer_profile,
        product=product
    )

    if not created:
        # Если уже был в избранном - удаляем
        favorite.delete()
        status = 'removed'
    else:
        status = 'added'

    # Получаем общее количество избранных товаров
    favorite_count = FavoriteProduct.objects.filter(user=customer_profile).count()

    return JsonResponse({
        'status': status,
        'count': favorite_count
    })


def ContactsView(request):
    """Контакты"""
    # Получаем все филиалы для отображения в контактах
    stores = Store.objects.all().order_by('city', 'address')

    context = {
        'stores': stores,
    }
    return render(request, 'basement/сontacts.html', context)


# Дополнительные служебные функции
@login_required
def dashboard_stats(request):
    """Статистика для дашборда (может пригодиться для менеджера)"""
    if request.user.role != 'MANAGER':
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    # Статистика по товарам
    total_products = Product.objects.count()
    available_products = Product.objects.filter(available=True).count()
    unavailable_products = Product.objects.filter(available=False).count()

    # Статистика по категориям
    categories_stats = Category.objects.annotate(
        product_count=Count('product')
    ).values('name', 'product_count')

    # Статистика по филиалам
    stores_stats = Store.objects.annotate(
        product_count=Count('product')
    ).values('city', 'address', 'product_count')

    stats = {
        'total_products': total_products,
        'available_products': available_products,
        'unavailable_products': unavailable_products,
        'categories_stats': list(categories_stats),
        'stores_stats': list(stores_stats),
    }

    return JsonResponse(stats)


@login_required
def update_product_availability(request):
    """Обновление доступности товара (для менеджера)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)

    if request.user.role != 'MANAGER':
        return JsonResponse({'error': 'Доступ только для менеджеров'}, status=403)

    product_id = request.POST.get('product_id')
    available = request.POST.get('available') == 'true'

    try:
        product = Product.objects.get(id=product_id)
        product.available = available
        product.save()

        return JsonResponse({
            'status': 'success',
            'available': product.available
        })

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Товар не найден'}, status=404)


def search_suggestions(request):
    """AJAX-подсказки для поиска"""
    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    # Ищем товары по названию
    products = Product.objects.filter(
        name__icontains=query,
        available=True
    ).values('id', 'name')[:10]

    # Ищем категории
    categories = Category.objects.filter(
        name__icontains=query
    ).values('id', 'name')[:5]

    suggestions = {
        'products': list(products),
        'categories': list(categories),
    }

    return JsonResponse(suggestions)


def featured_products(request):
    """Рекомендованные товары (может использоваться на главной)"""
    # Берем случайные доступные товары
    available_products = list(Product.objects.filter(available=True))

    if len(available_products) > 6:
        featured = random.sample(available_products, 6)
    else:
        featured = available_products

    # Получаем список избранных товаров для авторизованного пользователя
    user_favorites = []
    if request.user.is_authenticated and request.user.role == 'CUSTOMER' and hasattr(request.user, 'customer_profile'):
        user_favorites = FavoriteProduct.objects.filter(
            user=request.user.customer_profile
        ).values_list('product_id', flat=True)

    context = {
        'featured_products': featured,
        'user_favorites': list(user_favorites),
    }

    return render(request, 'partials/featured_products.html', context)