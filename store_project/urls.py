#urls
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
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView

from store_app.views.auth_views import login_view, CustomerSignUpView, ManagerSignUpView
from store_app.views.dashboard_views import manager_dashboard, get_stores_by_city, \
    customer_profile, home, ContactsView, buy_page, sell_page
from store_app.views.favorite_views import favorites_view, toggle_favorite
from store_app.views.product_views import create_product, delete_products, \
    deactivate_products, edit_product, product_detail # product_list,
from store_project import settings

urlpatterns = [
    path('', home, name='home'),
    path('buy/', buy_page, name='buy'),
    path('sell/', sell_page, name='sell'),

    path('get-stores/', get_stores_by_city, name='get_stores_by_city'),

    path('login/', login_view, name='login'), # Вход пользователя.
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),  # Разлогиниться.
    path('signup/', CustomerSignUpView.as_view(), name='signup'),  # Сортирует пользователя, направляет на его стр.
    path('signup/customer/', CustomerSignUpView.as_view(), name='customer_signup'), # Регистрация покупателя.  (Не используется)
    path('signup/manager/', ManagerSignUpView.as_view(), name='manager_signup'),  # Регистрация менеджера(панель админа).

    # Подвал
    path('home/contacts/', ContactsView, name='contacts_view'), # Филиалы
    path('privacy/', TemplateView.as_view(template_name='templates/basement/privacy.html'), name='privacy_policy'),  # (Не используется)

    # Dashboard URLs
    path('manager/dashboard/', manager_dashboard, name='manager_dashboard'),  # Отображает страницу менеджера.
    # Не используется пока.
    path('customer/dashboard/', customer_profile, name='customer_dashboard'), # Отображает страницу покупателя.

    # Product URLs
    path('manager/create-product/', create_product, name='create_product'), # Создание продукта.
    path('product/<int:id>/<slug:slug>/', product_detail, name='product_detail'),  # Просмотр продукта.
    path('product/edit/<int:pk>/', edit_product, name='edit_product'),  # Редактирование продукта.
    path('manager/delete-products/', delete_products, name='delete_products'), # Удаление продукта.
    path('manager/deactivate-products/', deactivate_products, name='deactivate_products'), # Снять с продажи.

    # Favorites URLs
    path('favorites/', favorites_view, name='favorites'),  # Для просмотра избранного
    path('favorites/toggle/', toggle_favorite, name='toggle_favorite'),  # Для добавления/удален

    # Admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
