"""
URL configuration for store_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView

from store_app.views.auth_views import login_view, CustomerSignUpView, ManagerSignUpView
from store_app.views.cart_views import cart_view, add_to_cart
from store_app.views.dashboard_views import customer_dashboard, manager_dashboard
from store_app.views.favorite_views import favorites_view
from store_app.views.product_views import product_list, product_detail


urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', login_view, name='login'), # Вход пользователя.
    # path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', CustomerSignUpView.as_view(), name='signup'),  # Сортирует пользователя, направляет на его стр.
    path('signup/customer/', CustomerSignUpView.as_view(), name='customer_signup'), # Регистрация покупателя.
    path('signup/manager/', ManagerSignUpView.as_view(), name='manager_signup'),  # Регистрация менеджера.

    # Dashboard URLs
    # Неиспользуется
    path('customer/dashboard/', customer_dashboard, name='customer_dashboard'), # Отображает страницу покупателя.

    path('manager/dashboard/', manager_dashboard, name='manager_dashboard'),  # Отображает страницу менеджера.

    # Product URLs
    path('products/', product_list, name='product_list'), # Список продуктов
    path('products/<slug:category_slug>/', product_list, name='product_list_by_category'), # Список прод по категории.
    path('product/<int:id>/<slug:slug>/', product_detail, name='product_detail'),  # Детали продукта

    # Favorites URLs
    path('products/favorites/', favorites_view, name='favorites'),  # Избранные товары

    # Cart URLs
    path('cart/', cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),

    # Profile URLs
    # path('profile/', customer_profile, name='customer_profile'),
    # path('orders/history/', order_history, name='order_history'),

    # Admin
    path('admin/', admin.site.urls),
]
