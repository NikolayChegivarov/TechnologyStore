from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from store_app.models import Product, FavoriteProduct


@login_required
def favorites_view(request):
    """Отображение страницы с избранными товарами"""
    if request.user.role != 'CUSTOMER':
        return render(request, 'error.html', {'message': 'Доступ запрещен'}, status=403)

    favorites = FavoriteProduct.objects.filter(user=request.user.customer_profile)
    return render(request, 'favorites.html', {'favorites': favorites})


@require_http_methods(["POST"])
@login_required
def toggle_favorite(request):
    """Добавление/удаление товара из избранного (AJAX)"""
    if request.user.role != 'CUSTOMER':
        return JsonResponse({'status': 'error', 'message': 'Доступ запрещен'}, status=403)

    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'status': 'error', 'message': 'Не указан ID товара'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
        customer = request.user.customer_profile
    except (Product.DoesNotExist, AttributeError):
        return JsonResponse({'status': 'error', 'message': 'Товар не найден'}, status=404)

    favorite, created = FavoriteProduct.objects.get_or_create(
        user=customer,
        product=product
    )

    if not created:
        favorite.delete()
        action = 'removed'
    else:
        action = 'added'

    count = FavoriteProduct.objects.filter(user=customer).count()
    return JsonResponse({
        'status': action,
        'count': count,
        'product_id': product_id
    })