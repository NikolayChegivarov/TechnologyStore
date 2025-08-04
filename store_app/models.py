from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from enum import Enum


phone_validator = RegexValidator(
    regex=r'^\+?[0-9\s-]+$',
    message='Номер телефона должен содержать только цифры, пробелы и знак +'
)

class Store(models.Model):  # Филиалы
    city = models.CharField(max_length=255, db_index=True)
    address = models.TextField(
        blank=True,
        verbose_name="Адрес",
        validators=[RegexValidator(
            regex=r'^[а-яА-ЯёЁ0-9\s.,-]+$',
            message='Допустимы русские буквы, цифры, пробелы и знаки .,-'
        )]
    )
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
    # Валидатор на русский
    cyrillic_validator = RegexValidator(
        regex=r'^[а-яА-ЯёЁ\\s-]+$',
        message='Допустимы только русские буквы, пробелы и дефисы'
    )
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, related_name='managers')
    last_name = models.CharField(
        max_length=100,
        verbose_name="Фамилия",
        validators=[cyrillic_validator]
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name="Имя",
        validators=[cyrillic_validator]
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Отчество",
        validators=[cyrillic_validator]
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        validators=[phone_validator]
    )
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
    # Общий валидатор для кириллицы, пробелов и дефисов
    cyrillic_validator = RegexValidator(
        regex=r'^[а-яА-ЯёЁ\s-]+$',
        message='Допустимы только русские буквы, пробелы и дефисы.'
    )
    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Логин",
        help_text="Уникальный идентификатор пользователя (можно использовать латиницу)"
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name="Фамилия",
        validators=[cyrillic_validator]
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name="Имя",
        validators=[cyrillic_validator]
    )
    middle_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Отчество",
        validators=[cyrillic_validator]
    )
    email = models.EmailField(
        max_length=50,
        null=True,
        verbose_name="Почта"
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        validators=[phone_validator]
    )
    address = models.TextField(
        blank=True,
        verbose_name="Адрес",
        validators=[RegexValidator(
            regex='^[а-яА-ЯёЁ0-9\s.,-]+$',
            message='Допустимы русские буквы, цифры, пробелы и знаки .,-'
        )]
    )
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
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[а-яА-ЯёЁa-zA-Z0-9@.+\-_\s]+$',
            message='Логин может содержать русские/латинские буквы, цифры и @/./+/-/_'
        )]
    )
    # Валидатор для кириллицы, пробелов и дефисов
    cyrillic_validator = RegexValidator(
        regex='^[а-яА-ЯёЁ\\s-]+$',
        message='Допустимы только русские буквы, пробелы и дефисы'
    )

    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
        validators=[cyrillic_validator]
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
        validators=[cyrillic_validator]
    )

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
        creating = not self.pk
        super().save(*args, **kwargs)

        if self.role == User.Role.MANAGER and self.manager_profile:
            self.manager_profile.first_name = self.first_name
            self.manager_profile.last_name = self.last_name
            self.manager_profile.save()


class Product(models.Model):  # Продукт
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)  # описание
    price = models.DecimalField(max_digits=10, decimal_places=2)  # цена
    available = models.BooleanField(default=True)  # наличие
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')  # филиал
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

class FavoriteProduct(models.Model):  # Избранные товары
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='favorite_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Избранный товар"
        verbose_name_plural = "Избранные товары"
        ordering = ['-added_at']
        unique_together = ('user', 'product')  # один и тот же товар нельзя добавить дважды
        indexes = [
            models.Index(fields=['user', 'product']),
        ]

    def __str__(self):
        return f"{self.user} — {self.product}"


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
