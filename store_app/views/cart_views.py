# Корзина добавление / содержание
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Product
from django.views.decorators.http import require_POST

@require_POST
def add_to_cart(request, product_id):
    """Обрабатывает добавление товара в корзину:
    - Доступен только для POST-запросов (защита от случайных переходов)
    - Находит товар по ID или возвращает 404 если не существует
    - Добавляет товар в корзину (сессию пользователя)
    - Перенаправляет на страницу просмотра корзины

    Args:
        product_id (int): ID товара для добавления в корзину

    Returns:
        HttpResponseRedirect: Перенаправление на страницу корзины
    """
    product = get_object_or_404(Product, id=product_id)
    # Логика добавления в корзину
    return redirect('cart_view')

def cart_view(request):
    """Отображает содержимое корзины пользователя:
    - Показывает все добавленные товары
    - Отображает общую стоимость
    - Предоставляет интерфейс для изменения количества/удаления
    - Использует шаблон cart/detail.html

    Returns:
        HttpResponse: Отображение страницы корзины
    """
    # Логика отображения корзины
    return render(request, 'cart/detail.html')