import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from store_app.models import Product, FavoriteProduct

User = get_user_model()


@pytest.mark.django_db
class TestCreateProductView:
    """Тесты для create_product view"""

    def test_create_product_requires_manager_role(self, client):
        """Тест что создание товара требует роли MANAGER"""
        # Анонимный пользователь - должен редиректить на логин
        response = client.get(reverse('create_product'))
        assert response.status_code == 302
        assert response.url.startswith('/login/')

        # Пользователь с ролью CUSTOMER - должен возвращать 403
        user = User.objects.create_user(
            username='customer',
            password='testpass123',
            role=User.Role.CUSTOMER
        )
        client.force_login(user)
        response = client.get(reverse('create_product'))
        assert response.status_code == 403

    def test_create_product_get_form(self, client, test_manager_with_user):
        """Тест отображения формы создания товара для менеджера"""
        user, manager = test_manager_with_user
        client.force_login(user)
        response = client.get(reverse('create_product'))
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'product/create_product.html' in [t.name for t in response.templates]

    def test_create_product_with_image(self, client, test_manager_with_user, test_category, test_store, temp_image):
        """Тест создания товара с изображением"""
        user, manager = test_manager_with_user
        client.force_login(user)

        post_data = {
            'name': 'Тестовый товар с картинкой',
            'description': 'Описание тестового товара',
            'price': 1000,
            'category': test_category.id,
            'store': test_store.id,
            'available': True,
        }

        # Создаем временный файл изображения для теста
        with open(temp_image, 'rb') as img:
            post_data['image'] = img

            response = client.post(reverse('create_product'), post_data)

        assert response.status_code == 200
        assert 'success_message' in response.context
        assert Product.objects.filter(name='Тестовый товар с картинкой').exists()

    def test_create_product_without_image(self, client, test_manager_with_user, test_category, test_store):
        """Тест создания товара без изображения"""
        user, manager = test_manager_with_user
        client.force_login(user)

        post_data = {
            'name': 'Тестовый товар без картинки',
            'description': 'Описание тестового товара',
            'price': 1000,
            'category': test_category.id,
            'store': test_store.id,
            'available': True,
        }

        response = client.post(reverse('create_product'), post_data)
        assert response.status_code == 200
        assert Product.objects.filter(name='Тестовый товар без картинки').exists()