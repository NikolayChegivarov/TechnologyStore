import sys

sys.stderr.flush()
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Manager, Store, Category, ActionLog, PageView, WorkingHours

from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta


class WorkingHoursInline(admin.TabularInline):
    """Редактирование расписания"""
    model = WorkingHours
    extra = 0
    min_num = 7  # Все дни недели
    max_num = 7
    can_delete = False

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Устанавливаем дни недели по порядку
        if obj and not obj.working_hours.exists():
            for day in range(7):
                WorkingHours.objects.get_or_create(
                    store=obj,
                    day_of_week=day,
                    defaults={
                        'opening_time': None,
                        'closing_time': None,
                        'is_closed': True
                    }
                )
        return formset


class WorkingHoursAdmin(admin.ModelAdmin):
    """Управления расписанием"""
    list_display = ('store', 'day_of_week_display', 'opening_time', 'closing_time', 'is_closed', 'is_open_today')
    list_filter = ('store', 'day_of_week', 'is_closed')
    search_fields = ('store__city', 'store__address')
    ordering = ('store', 'day_of_week')

    fieldsets = (
        (None, {
            'fields': ('store', 'day_of_week')
        }),
        ('Время работы', {
            'fields': ('opening_time', 'closing_time', 'is_closed'),
            'description': 'Укажите время работы или отметьте как выходной'
        }),
    )

    def day_of_week_display(self, obj):
        return obj.get_day_of_week_display()

    day_of_week_display.short_description = 'День недели'

    def is_open_today(self, obj):
        """Показывает, открыт ли магазин сегодня по этому расписанию"""
        if obj.is_closed:
            return "❌ Выходной"

        today = timezone.now().weekday()
        if obj.day_of_week == today:
            current_time = timezone.now().time()
            if obj.opening_time <= current_time <= obj.closing_time:
                return "✅ Открыт сейчас"
            return "⏰ Закрыт сейчас"
        return "📅 По расписанию"

    is_open_today.short_description = 'Статус сегодня'


class CategoryAdmin(admin.ModelAdmin):
    """Управления категориями товаров:"""
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
    """Управления магазинами (филиалами):"""
    list_display = ('city', 'address', 'latitude', 'longitude', 'created_at', 'updated_at', 'is_open_now_display')
    search_fields = ('city', 'address')
    list_filter = ('city', 'created_at')
    ordering = ('city', 'address')

    # Добавляем встроенное редактирование расписания
    inlines = [WorkingHoursInline]

    fieldsets = (
        (None, {
            'fields': ('city', 'address')
        }),
        ('Координаты для карты', {
            'fields': ('latitude', 'longitude'),
            'description': 'Координаты для отображения на карте. Можно оставить пустыми.'
        }),
        ('Дополнительная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def is_open_now_display(self, obj):
        """Отображает статус магазина прямо в списке"""
        if obj.is_open_now():
            return "✅ Открыт"
        return "❌ Закрыт"

    is_open_now_display.short_description = 'Статус сейчас'


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
    """Журнал действий пользователей с товарами."""
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
    """Статистика посещений сайта"""
    list_display = ('url', 'user', 'ip_address', 'timestamp', 'duration', 'is_manager_visit')
    list_filter = ('timestamp', 'url', 'user__role')
    readonly_fields = ('timestamp', 'duration', 'user_agent')
    date_hierarchy = 'timestamp'
    change_list_template = "admin/analytics/pageview/change_list.html"

    def is_manager_visit(self, obj):
        """Показывает, является ли посещение от менеджера"""
        manager_ips = PageView.get_manager_ips()
        if obj.ip_address in manager_ips:
            return "✅ Менеджер"
        return "👤 Клиент"

    is_manager_visit.short_description = "Тип посетителя"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Статистика за сегодня
        today_visitors = PageView.get_today_unique_visitors()

        # Статистика за последние 30 дней
        visitor_stats = PageView.get_unique_visitors_stats(days=30)

        # Дополнительная статистика
        total_visits = PageView.objects.count()
        manager_ips = PageView.get_manager_ips()
        manager_visits = PageView.objects.filter(ip_address__in=manager_ips).count()
        client_visits = total_visits - manager_visits

        extra_context.update({
            'title': "Статистика посещений",
            'today_visitors': today_visitors,
            'visitor_stats': visitor_stats,
            'total_visits': total_visits,
            'manager_visits': manager_visits,
            'client_visits': client_visits,
            'total_days': len(visitor_stats),
        })

        return super().changelist_view(request, extra_context=extra_context)


# Регистрируем все модели ЕДИНООБРАЗНО через admin.site.register()
admin.site.register(Category, CategoryAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ActionLog, ActionLogAdmin)
admin.site.register(PageView, PageViewAdmin)
admin.site.register(WorkingHours, WorkingHoursAdmin)  # Добавляем новую админ-панель