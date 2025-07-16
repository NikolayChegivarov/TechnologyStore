# Список товаров / Детали товара.
from django.shortcuts import render, get_object_or_404
from ..models import Product, Category


def product_list(request, category_slug=None):
    """Отображает список товаров с возможностью фильтрации по категории:
    - Получает все доступные товары (available=True)
    - Если передан category_slug, фильтрует товары по категории
    - Возвращает список всех категорий для навигации
    - Использует шаблон product/list.html

    Args:
        category_slug (str, optional): Слаг категории для фильтрации товаров
    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })


def product_detail(request, id, slug):
    """Отображает детальную страницу товара:
    - Находит товар по id и slug (двойная проверка URL)
    - Проверяет, что товар доступен (available=True)
    - Возвращает 404 если товар не найден или недоступен
    - Использует шаблон product/detail.html

    Args:
        id (int): ID товара в базе данных
        slug (str): ЧПУ-название товара
    """
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'product/detail.html', {'product': product})