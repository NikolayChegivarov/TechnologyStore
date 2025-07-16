from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from enum import Enum


class Store(models.Model):  # Филиалы
    city = models.CharField(max_length=255, db_index=True)
    address = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.city}, {self.address}"

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"
        ordering = ['city', 'address']
        indexes = [
            models.Index(fields=['city', 'address']),
        ]


class Category(models.Model):    # Категории
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


class Manager(models.Model):  # Продавец
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, related_name='managers')
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    is_active = models.BooleanField(default=True, verbose_name="Доступ разрешен")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    class Meta:
        verbose_name = "Продавец"
        verbose_name_plural = "Продавцы"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
        ]


class Customer(models.Model):  # Покупатель
    username = models.CharField(max_length=50, unique=True)
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    imail = models.CharField(max_length=50, verbose_name="Почта")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    address = models.TextField(blank=True, verbose_name="Адрес")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['phone']),
        ]


class User(AbstractUser):  # Пользователь

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        CUSTOMER = 'CUSTOMER', 'Customer'

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    # Связи с существующими моделями
    manager_profile = models.OneToOneField(
        Manager,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_account'
    )
    customer_profile = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_account'
    )

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = User.Role.ADMIN
        elif not self.pk:  # только при создании
            self.role = self.role or User.Role.CUSTOMER
        super().save(*args, **kwargs)


class Product(models.Model):  # Продукт
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    created_by = models.ForeignKey(
        Manager,
        on_delete=models.PROTECT,
        related_name='products_created',
        verbose_name='Создатель товара'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name', 'price']
        indexes = [
            models.Index(fields=['name', 'price']),
        ]


class CartItem(models.Model):  # Корзина
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'product']),
        ]


class OrderStatus(Enum):  # Статус заказа
    PENDING = "pending"  # в ожидании
    PROCESSING = "processing"  # в обработке
    SHIPPED = "shipped"  # отправленный
    DELIVERED = "delivered"  # доставленный
    CANCELLED = "cancelled"  # отменено

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Order(models.Model):  # Заказ
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    salesman = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, related_name='orders_processed')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=OrderStatus.choices(), default=OrderStatus.PENDING.value)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]


class OrderItem(models.Model):  # Элемент заказа
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
