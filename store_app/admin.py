from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Manager, Store, Category, ActionLog, PageView

from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta


class CategoryAdmin(admin.ModelAdmin):
    """Админ-панель для управления категориями товаров:"""
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Дополнительная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class StoreAdmin(admin.ModelAdmin):
    """Админ-интерфейс для управления магазинами (филиалами):"""
    list_display = ('city', 'address', 'created_at', 'updated_at')
    search_fields = ('city', 'address')
    list_filter = ('city', 'created_at')
    ordering = ('city', 'address')

    fieldsets = (
        (None, {
            'fields': ('city', 'address')
        }),
        ('Дополнительная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


class CustomUserAdmin(UserAdmin):
    """
    Кастомный админ-класс для модели User в Django-админке:
    """
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональные данные', {
            'fields': (
                ('last_name', 'first_name'),
                'email'
            ),
            'description': "Указывайте данные на русском языке"
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
    # Добавляем подсказки для полей
    help_texts = {
        'username': 'Логин для входа в систему',
        'first_name': 'Только русские буквы и дефисы',
        'last_name': 'Только русские буквы и дефисы',
        'role': 'Выберите роль пользователя (ADMIN, MANAGER или CUSTOMER)',
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Устанавливаем роль MANAGER по умолчанию для новых пользователей
        if not obj and 'role' in form.base_fields:
            form.base_fields['role'].initial = User.Role.MANAGER
        return form

    def save_model(self, request, obj, form, change):
        """Создает профиль менеджера при необходимости"""
        # При сохранении суперпользователя устанавливаем роль ADMIN
        if obj.is_superuser:
            obj.role = User.Role.ADMIN

        super().save_model(request, obj, form, change)

        # Создаем профиль менеджера если его нет
        if obj.role == User.Role.MANAGER and not obj.manager_profile:
            manager = Manager.objects.create(
                first_name=obj.first_name,
                last_name=obj.last_name,
                phone='',
                position='MANAGER',
                is_active=True
            )
            obj.manager_profile = manager
            obj.save()


class ActionLogAdmin(admin.ModelAdmin):
    """Админ-панель для журнала действий пользователей с товарами."""
    list_display = ('user', 'action_type', 'product_name', 'product_id', 'timestamp', 'format_changed_fields')
    list_filter = ('action_type', 'user', 'timestamp')
    search_fields = ('product_name', 'user__username')
    readonly_fields = ('timestamp', 'changed_fields')
    date_hierarchy = 'timestamp'

    def format_changed_fields(self, obj):
        if not obj.changed_fields:
            return "-"
        return ", ".join([
            f"{field}: {values['old']} → {values['new']}"
            for field, values in obj.changed_fields.items()
        ])
    format_changed_fields.short_description = "Изменённые поля"


class PageViewAdmin(admin.ModelAdmin):
    """Админ-панель для статистики посещений сайта"""
    list_display = ('url', 'user', 'ip_address', 'timestamp', 'duration')
    list_filter = ('timestamp', 'url')
    readonly_fields = ('timestamp', 'duration', 'user_agent')
    date_hierarchy = 'timestamp'

    def changelist_view(self, request, extra_context=None):
        # Добавляем статистику в контекст
        extra_context = extra_context or {}

        # Статистика за последние 30 дней
        thirty_days_ago = timezone.now() - timedelta(days=30)

        stats = {
            'total_visits': PageView.objects.count(),
            'unique_visitors': PageView.objects.values('session_key').distinct().count(),
            'avg_duration': PageView.objects.aggregate(avg=Avg('duration'))['avg'] or 0,
            'recent_visits': PageView.objects.filter(timestamp__gte=thirty_days_ago).count(),
            'popular_pages': PageView.objects.values('url').annotate(
                visits=Count('id')
            ).order_by('-visits')[:10],
        }

        extra_context['stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)


# Регистрируем все модели ЕДИНООБРАЗНО через admin.site.register()
admin.site.register(Category, CategoryAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ActionLog, ActionLogAdmin)
admin.site.register(PageView, PageViewAdmin)