# Список товаров / Детали товара / Создание товара
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..forms.create_product_form import CreateProductForm
from ..models import Product, Category, ActionLog
from django.contrib import messages


def create_product(request):
    """Обрабатывает создание нового товара:
    - Проверяет аутентификацию пользователя и его роль (только MANAGER)
    - При GET-запросе отображает пустую форму создания товара
    - При POST-запросе валидирует форму и сохраняет товар, привязывая к менеджеру
    - В случае успеха отображает форму с сообщением об успешном создании и данными товара
    - Использует шаблон create_product.html

    Args:
        request (HttpRequest): Объект запроса

    Returns:
        HttpResponse: Ответ с формой или редирект для неавторизованных пользователей
    """
    if not request.user.is_authenticated or request.user.role != 'MANAGER':
        return redirect('login')

    success_message = None
    created_product = None

    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user.manager_profile
            product.save()  # Автоматически генерирует slug

            # Убедимся, что slug не пустой
            if not product.slug:
                product.slug = f"product-{product.id}"
                product.save()

            success_message = f"Товар '{product.name}' успешно создан!"
            created_product = product
            # Не делаем редирект, а рендерим ту же страницу с сообщением
    else:
        form = CreateProductForm()

    context = {
        'form': form,
        'success_message': success_message,
        'created_product': created_product
    }
    return render(request, 'product/create_product.html', context)


def delete_products(request):
    """Удаляет продукт(ы)."""
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')

        # Логирование перед удалением
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            ActionLog.objects.create(
                user=request.user,
                action_type='DELETE',
                product_name=product.name,
                product_id=product.id,
                details=f"Товар удален: {product.name}"
            )

        products.delete()
        messages.success(request, f'Удалено товаров: {len(product_ids)}')
        return redirect('manager_dashboard')
    return redirect('manager_dashboard')


def deactivate_products(request):
    """Меняет статус продукта, убирая ищ наличия.
    Продукт становится не доступен для пользователя сайтом."""
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        Product.objects.filter(id__in=product_ids).update(available=False)
        return redirect('manager_dashboard')
    return redirect('manager_dashboard')


# def product_list(request, category_slug=None):
#     """Отображает список товаров с возможностью фильтрации по категории:
#     - Получает все доступные товары (available=True)
#     - Если передан category_slug, фильтрует товары по категории
#     - Возвращает список всех категорий для навигации
#     - Использует шаблон product/list.html
#
#     Args:
#         category_slug (str, optional): Слаг категории для фильтрации товаров
#     """
#     category = None
#     categories = Category.objects.all()
#     products = Product.objects.filter(available=True)
#
#     if category_slug:
#         category = get_object_or_404(Category, slug=category_slug)
#         products = products.filter(category=category)
#
#     return render(request, 'product/list.html', {
#         'category': category,
#         'categories': categories,
#         'products': products
#     })


def product_detail(request, id, slug):
    """Отображает детальную страницу товара:
    - Находит товар по id и slug (двойная проверка URL)
    - Для менеджеров показывает любой товар (даже со статусом нет в наличии)
    - Для клиентов показывает только товары со статусом доступен для продажи.
    """
    if request.user.is_authenticated and request.user.role == 'MANAGER':
        product = get_object_or_404(Product, id=id, slug=slug)
    else:
        product = get_object_or_404(Product, id=id, slug=slug, available=True)

    return render(request, 'product/detail_product.html', {
        'product': product,
        'user': request.user  # Убедитесь, что user передается в контекст
    })


def edit_product(request, pk):
    """Изменяет продукт."""
    if request.user.role != 'MANAGER':
        return redirect('login')

    product = get_object_or_404(Product, pk=pk)
    old_values = {
        'name': product.name,
        'price': str(product.price),
        'available': product.available,
        'description': product.description,
        # Добавьте другие поля, если нужно
    }

    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            updated_product = form.save()

            # Сравниваем старые и новые значения
            changed_fields = {}
            for field in ['name', 'price', 'available', 'description']:
                old_value = old_values[field]
                new_value = str(getattr(updated_product, field))
                if old_value != new_value:
                    changed_fields[field] = {
                        'old': old_value,
                        'new': new_value
                    }

            # Логирование
            ActionLog.objects.create(
                user=request.user,
                action_type='EDIT',
                product_name=updated_product.name,
                product_id=updated_product.id,
                changed_fields=changed_fields,
                details=f"Изменены поля: {', '.join(changed_fields.keys())}"
            )

            messages.success(request, f'Товар "{updated_product.name}" успешно обновлен!')
            return redirect('product_detail', id=updated_product.id, slug=updated_product.slug)
    else:
        form = CreateProductForm(instance=product)

    return render(request, 'product/edit_product.html', {
        'form': form,
        'product': product
    })