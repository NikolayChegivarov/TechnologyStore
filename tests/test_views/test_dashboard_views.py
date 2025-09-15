# tests/test_views/test_dashboard_views.py
import pytest
from django.urls import reverse
from django.test import RequestFactory
from store_app.models import Product, Store, Category, FavoriteProduct
from store_app.views.dashboard_views import manager_dashboard, home, get_stores_by_city


@pytest.mark.django_db
class TestCustomerDashboard:
    """Тесты для customer_dashboard view"""

    def test_customer_dashboard_requires_login(self, client):
        """Тест что customer_dashboard требует аутентификации"""
        response = client.get(reverse('customer_dashboard'))
        assert response.status_code == 302
        assert response.url.startswith('/auth/login/')

    def test_customer_dashboard_authenticated(self, client, customer_user):
        """Тест customer_dashboard для аутентифицированного пользователя"""
        client.force_login(customer_user)
        response = client.get(reverse('customer_dashboard'))
        assert response.status_code == 200
        assert 'dashboard/customer.html' in [t.name for t in response.templates]


@pytest.mark.django_db
class TestManagerDashboard:
    """Тесты для manager_dashboard view"""

    def test_manager_dashboard_requires_login(self, client):
        """Тест что manager_dashboard требует аутентификации"""
        response = client.get(reverse('manager_dashboard'))
        assert response.status_code == 302
        assert response.url.startswith('/auth/login/')

    def test_manager_dashboard_authenticated(self, client, manager_user):
        """Тест manager_dashboard для аутентифицированного менеджера"""
        client.force_login(manager_user)
        response = client.get(reverse('manager_dashboard'))
        assert response.status_code == 200
        assert 'dashboard/manager.html' in [t.name for t in response.templates]

    def test_manager_dashboard_filtering(self, client, manager_user, store, category):
        """Тест фильтрации товаров в manager_dashboard"""
        client.force_login(manager_user)

        # Тест фильтра по магазину
        response = client.get(f"{reverse('manager_dashboard')}?store={store.id}")
        assert response.status_code == 200

        # Тест фильтра по категории
        response = client.get(f"{reverse('manager_dashboard')}?category={category.id}")
        assert response.status_code == 200

        # Тест сортировки
        response = client.get(f"{reverse('manager_dashboard')}?sort=newest")
        assert response.status_code == 200


@pytest.mark.django_db
class TestHomeView:
    """Тесты для home view"""

    def test_home_view_anonymous(self, client):
        """Тест home view для анонимного пользователя"""
        response = client.get(reverse('home'))
        assert response.status_code == 200
        assert 'home.html' in [t.name for t in response.templates]

    def test_home_view_with_filters(self, client, store, category):
        """Тест home view с фильтрами"""
        # Тест фильтра по городу
        response = client.get(f"{reverse('home')}?city={store.city}")
        assert response.status_code == 200

        # Тест фильтра по магазину
        response = client.get(f"{reverse('home')}?store={store.id}")
        assert response.status_code == 200

        # Тест фильтра по категории
        response = client.get(f"{reverse('home')}?category={category.id}")
        assert response.status_code == 200

    def test_home_view_random_products(self, client, product_factory):
        """Тест что home view показывает случайные товары без фильтров"""
        # Создаем больше 12 товаров
        product_factory.create_batch(15, available=True)

        response = client.get(reverse('home'))
        assert response.status_code == 200
        assert len(response.context['products']) == 12

    def test_home_view_with_favorites(self, client, customer_user, product):
        """Тест home view с избранными товарами для авторизованного пользователя"""
        client.force_login(customer_user)

        # Добавляем товар в избранное
        FavoriteProduct.objects.create(
            user=customer_user.customer_profile,
            product=product
        )

        response = client.get(reverse('home'))
        assert response.status_code == 200
        assert product.id in response.context['user_favorites']


@pytest.mark.django_db
class TestGetStoresByCity:
    """Тесты для get_stores_by_city view"""

    def test_get_stores_by_city(self, client, store):
        """Тест получения магазинов по городу"""
        response = client.get(f"{reverse('get_stores_by_city')}?city={store.city}")
        assert response.status_code == 200
        assert response.json()['stores'][0]['id'] == store.id

    def test_get_stores_by_city_empty(self, client):
        """Тест получения магазинов для несуществующего города"""
        response = client.get(f"{reverse('get_stores_by_city')}?city=Nonexistent")
        assert response.status_code == 200
        assert len(response.json()['stores']) == 0