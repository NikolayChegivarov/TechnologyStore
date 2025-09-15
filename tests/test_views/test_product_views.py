import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from store_app.models import Product, FavoriteProduct

User = get_user_model()


@pytest.mark.django_db
class TestCustomerDashboard:
    """Тесты для customer_dashboard view"""

    def test_customer_dashboard_requires_login(self, client):
        """Тест что customer_dashboard требует аутентификации"""
        response = client.get(reverse('customer_dashboard'))
        assert response.status_code == 302
        assert response.url.startswith('/login/')

    def test_customer_dashboard_authenticated(self, client, test_customer_with_user):
        """Тест customer_dashboard для аутентифицированного пользователя"""
        user, customer = test_customer_with_user
        client.force_login(user)
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
        assert response.url.startswith('/login/')

    def test_manager_dashboard_authenticated(self, client, test_manager_with_user):
        """Тест manager_dashboard для аутентифицированного менеджера"""
        user, manager = test_manager_with_user
        client.force_login(user)
        response = client.get(reverse('manager_dashboard'))
        assert response.status_code == 200
        assert 'dashboard/manager.html' in [t.name for t in response.templates]

    def test_manager_dashboard_filtering(self, client, test_manager_with_user, test_store, test_category):
        """Тест фильтрации товаров в manager_dashboard"""
        user, manager = test_manager_with_user
        client.force_login(user)

        # Тест фильтра по магазину
        response = client.get(f"{reverse('manager_dashboard')}?store={test_store.id}")
        assert response.status_code == 200

        # Тест фильтра по категории
        response = client.get(f"{reverse('manager_dashboard')}?category={test_category.id}")
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

    def test_home_view_with_filters(self, client, test_store, test_category):
        """Тест home view с фильтрами"""
        # Тест фильтра по городу
        response = client.get(f"{reverse('home')}?city={test_store.city}")
        assert response.status_code == 200

        # Тест фильтра по магазину
        response = client.get(f"{reverse('home')}?store={test_store.id}")
        assert response.status_code == 200

        # Тест фильтра по категории
        response = client.get(f"{reverse('home')}?category={test_category.id}")
        assert response.status_code == 200

    def test_home_view_random_products(self, client, test_product, test_category, test_store, test_manager):
        """Тест что home view показывает случайные товары без фильтров"""
        # Создаем больше 12 товаров
        for i in range(14):
            Product.objects.create(
                category=test_category,
                name=f"Тестовый товар {i}",
                description=f"Описание тестового товара {i}",
                price=1000 + i * 100,
                available=True,
                store=test_store,
                created_by=test_manager
            )

        response = client.get(reverse('home'))
        assert response.status_code == 200
        assert len(response.context['products']) == 12

    def test_home_view_with_favorites(self, client, test_customer_with_user, test_product):
        """Тест home view с избранными товарами для авторизованного пользователя"""
        user, customer = test_customer_with_user
        client.force_login(user)

        # Добавляем товар в избранное
        FavoriteProduct.objects.create(
            user=customer,
            product=test_product
        )

        response = client.get(reverse('home'))
        assert response.status_code == 200
        assert test_product.id in response.context['user_favorites']


@pytest.mark.django_db
class TestGetStoresByCity:
    """Тесты для get_stores_by_city view"""

    def test_get_stores_by_city(self, client, test_store):
        """Тест получения магазинов по городу"""
        # Создаем временного пользователя для теста
        user = User.objects.create_user(
            username='test_user',
            password='testpass123',
            role=User.Role.CUSTOMER
        )
        client.force_login(user)

        response = client.get(f"{reverse('get_stores_by_city')}?city={test_store.city}")
        assert response.status_code == 200
        assert response.json()['stores'][0]['id'] == test_store.id

    def test_get_stores_by_city_empty(self, client):
        """Тест получения магазинов для несуществующего города"""
        # Создаем временного пользователя для теста
        user = User.objects.create_user(
            username='test_user',
            password='testpass123',
            role=User.Role.CUSTOMER
        )
        client.force_login(user)

        response = client.get(f"{reverse('get_stores_by_city')}?city=Nonexistent")
        assert response.status_code == 200
        assert len(response.json()['stores']) == 0