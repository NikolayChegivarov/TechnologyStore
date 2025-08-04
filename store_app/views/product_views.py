# Список товаров / Детали товара / Создание товара
from django.shortcuts import render, get_object_or_404, redirect

from ..forms.create_product_form import CreatProductForm
from ..models import Product, Category


def create_product(request):
    """Обрабатывает создание нового товара:
    - Проверяет аутентификацию пользователя и его роль (только MANAGER)
    - При GET-запросе отображает пустую форму создания товара
    - При POST-запросе валидирует форму и сохраняет товар, привязывая к менеджеру
    - В случае успеха отображает форму с сообщением об успешном создании
    - Использует шаблон create_product.html

    Args:
        request (HttpRequest): Объект запроса

    Returns:
        HttpResponse: Ответ с формой или редирект для неавторизованных пользователей
    """
    if not request.user.is_authenticated or request.user.role != 'MANAGER':
        return redirect('login')

    if request.method == 'POST':
        form = CreatProductForm(request.POST)
        if form.is_valid():
            # Создаем объект продукта, но пока не сохраняем в БД
            product = form.save(commit=False)
            # Устанавливаем создателя продукта
            product.created_by = request.user.manager_profile
            # Теперь сохраняем в БД
            product.save()

            # Подготавливаем контекст для отображения
            context = {
                'form': CreatProductForm(),  # Новая пустая форма
                'success_message': f'Товар "{product.name}" успешно создан!',
                'created_product': product  # Передаем созданный продукт
            }
            return render(request, 'create_product.html', context)
    else:
        form = CreatProductForm()

    return render(request, 'create_product.html', {'form': form})


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