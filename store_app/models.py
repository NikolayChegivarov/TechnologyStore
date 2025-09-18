# pytest tests/test_models/test_product_models.py -v
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
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


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="ЧПУ-ссылка",
        help_text="Уникальный идентификатор для URL"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]


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


class Customer(models.Model):  # Пользователь сайта
    # Валидатор для кириллицы, пробелов и дефисов (если имя будет указано)
    cyrillic_validator = RegexValidator(
        regex=r'^[а-яА-ЯёЁ\s-]+$',
        message='Допустимы только русские буквы, пробелы и дефисы.'
    )

    magic_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    token_created_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    # Основной идентификатор - EMAIL. Делаем его уникальным.
    email = models.EmailField(
        max_length=255,  # Увеличил длину, стандартная для EmailField
        unique=True,  # Делаем уникальным! Это будет логин.
        blank=False,  # Обязательное поле, но только при регистрации
        null=False,
        verbose_name="Email"
    )

    # Персональные данные - все НЕОБЯЗАТЕЛЬНЫЕ.
    # Пользователь может заполнить их позже в личном кабинете.
    last_name = models.CharField(
        max_length=50,
        blank=True,  # Делаем необязательным
        verbose_name="Фамилия",
        validators=[cyrillic_validator]
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,  # Делаем необязательным
        verbose_name="Имя",
        validators=[cyrillic_validator]
    )
    middle_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Отчество",
        validators=[cyrillic_validator]
    )
    phone = models.CharField(
        max_length=20,
        blank=True,  # Делаем необязательным
        verbose_name="Телефон",
        validators=[phone_validator]
    )
    address = models.TextField(
        blank=True,
        verbose_name="Адрес",
        validators=[RegexValidator(
            regex=r'^[а-яА-ЯёЁ0-9\s.,-]+$',
            message='Допустимы русские буквы, цифры, пробелы и знаки .,-'
        )]
    )

    # Служебные поля
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Добавьте это поле для хранения хэша пароля, если решите использовать пароли
    # password = models.CharField(max_length=128, blank=True)

    def __str__(self):
        # Если есть имя, выводим его. Если нет - email.
        if self.first_name or self.last_name:
            return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['email']  # Сортируем по email
        indexes = [
            models.Index(fields=['email']),  # Индекс на email, т.к. по нему будем искать
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
        # Хешируем пароль только если он не хеширован
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

        # Перенесем логику обновления менеджера в отдельный блок
        if self.role == User.Role.MANAGER and self.manager_profile:
            self.manager_profile.first_name = self.first_name
            self.manager_profile.last_name = self.last_name
            self.manager_profile.save()


class Product(models.Model):  # Продукт
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)  # описание
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message='Цена должна быть положительной')]
    )  # цена
    available = models.BooleanField(default=True)  # наличие
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')  # филиал
    image = models.ImageField(
        upload_to='products/',
        verbose_name='Изображение товара',
        blank=True,
        null=True
    )
    external_url = models.URLField(
        verbose_name='Ссылка на товар',
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(
        Manager,
        on_delete=models.PROTECT,
        related_name='products_created',
        verbose_name='Создатель товара'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name="ЧПУ-ссылка"
    )  # для читаемых ссылок

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:250]  # Ограничение длины
            unique_slug = base_slug
            num = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name', 'price']
        indexes = [
            models.Index(fields=['name', 'price']),
        ]
        unique_together = ('name', 'store')

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


class ActionLog(models.Model):
    ACTION_TYPES = [
        ('CREATE', 'Создание товара'),
        ('EDIT', 'Редактирование товара'),
        ('DELETE', 'Удаление товара'),
        ('DEACTIVATE', 'Снятие с продажи'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Менеджер"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name="Тип действия"
    )
    product_name = models.CharField(
        max_length=255,
        verbose_name="Название товара"
    )
    product_id = models.IntegerField(
        verbose_name="ID товара",
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата и время"
    )
    changed_fields = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name="Изменённые поля (JSON)"
    )
    details = models.TextField(
        blank=True,
        null=True,
        verbose_name="Дополнительная информация"
    )

    class Meta:
        verbose_name = "Лог действий"
        verbose_name_plural = "Логи действий"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} {self.get_action_type_display()} {self.product_name}"