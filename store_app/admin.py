import sys

sys.stderr.flush()
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.forms import BaseInlineFormSet
from django.utils.html import format_html
from .models import User, Manager, Store, Category, ActionLog, PageView, WorkingHours

from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta


# -------------------------- КАСТОМНЫЕ ФОРМЫ ДЛЯ РАСПИСАНИЯ -------------------------
class WorkingHoursForm(forms.ModelForm):
    """Кастомная форма для времени с предустановленными значениями"""

    opening_time = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('07:00:00', '07:00'),
            ('08:00:00', '08:00'),
            ('09:00:00', '09:00'),
            ('10:00:00', '10:00'),
            ('11:00:00', '11:00'),
        ],
        required=False,
        label='Время открытия'
    )

    closing_time = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('18:00:00', '18:00'),
            ('19:00:00', '19:00'),
            ('20:00:00', '20:00'),
            ('21:00:00', '21:00'),
            ('22:00:00', '22:00'),
        ],
        required=False,
        label='Время закрытия'
    )

    class Meta:
        model = WorkingHours
        fields = '__all__'


class WorkingHoursFormSet(BaseInlineFormSet):
    """Кастомный FormSet для автоматического создания дней недели"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')

        # Если это новый магазин (нет primary key)
        if instance is None or instance.pk is None:
            # Создаем начальные данные для всех дней недели
            self.initial = [
                {'day_of_week': day, 'is_closed': False}
                for day in range(7)
            ]
            self.extra = 7


class WorkingHoursInline(admin.TabularInline):
    """Режим работы в виде inline в магазине"""
    model = WorkingHours
    form = WorkingHoursForm
    formset = WorkingHoursFormSet
    extra = 7  # Показываем все 7 дней недели
    max_num = 7  # Не больше 7 дней
    can_delete = False

    def get_formset(self, request, obj=None, **kwargs):
        """Автоматически создаем все дни недели для нового магазина"""
        if obj is None or obj.pk is None:
            kwargs['formset'] = WorkingHoursFormSet
        return super().get_formset(request, obj, **kwargs)


class WorkingHoursAdmin(admin.ModelAdmin):
    """Управление расписанием"""
    form = WorkingHoursForm
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
            if obj.opening_time and obj.closing_time and obj.opening_time <= current_time <= obj.closing_time:
                return "✅ Открыт сейчас"
            return "⏰ Закрыт сейчас"
        return "📅 По расписанию"

    is_open_today.short_description = 'Статус сегодня'


class CategoryAdmin(admin.ModelAdmin):
    """Управление категориями товаров:"""
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
    """Управление магазинами (филиалами):"""
    list_display = ('city', 'address', 'latitude', 'longitude', 'created_at', 'updated_at', 'is_open_now_display', 'working_hours_preview')
    search_fields = ('city', 'address')
    list_filter = ('city', 'created_at')
    ordering = ('city', 'address')
    readonly_fields = ('created_at', 'updated_at', 'working_hours_preview')

    # Добавляем встроенное редактирование расписания с кастомной формой
    inlines = [WorkingHoursInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('city', 'address')
        }),
        ('Координаты для карты', {
            'fields': ('latitude', 'longitude'),
            'description': 'Координаты для отображения на карте. Можно оставить пустыми.'
        }),
        ('Режим работы', {
            'fields': ('working_hours_preview',),
            'classes': ('collapse', 'wide'),
            'description': 'Предпросмотр текущего расписания работы'
        }),
        ('Дополнительная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_open_now_display(self, obj):
        """Отображает статус магазина прямо в списке"""
        if obj.is_open_now():
            return format_html('<span style="color: green; font-weight: bold;">✅ Открыт</span>')
        return format_html('<span style="color: red; font-weight: bold;">❌ Закрыт</span>')

    is_open_now_display.short_description = 'Статус сейчас'

    def working_hours_preview(self, obj):
        """Предпросмотр режима работы"""
        if obj.pk:  # Проверяем, что магазин сохранен в БД
            hours = obj.working_hours.all().order_by('day_of_week')
            if not hours:
                return "Режим работы не установлен"

            html = '<div style="max-width: 400px; font-size: 12px;">'
            for hour in hours:
                if hour.is_closed:
                    status = "❌ Выходной"
                else:
                    open_time = hour.opening_time.strftime('%H:%M') if hour.opening_time else '--:--'
                    close_time = hour.closing_time.strftime('%H:%M') if hour.closing_time else '--:--'
                    status = f"✅ {open_time} - {close_time}"
                html += f'<div><strong>{hour.get_day_of_week_display()}:</strong> {status}</div>'
            html += '</div>'
            return format_html(html)
        return "Сначала сохраните магазин, чтобы установить режим работы"

    working_hours_preview.short_description = 'Текущий режим работы'

    def save_related(self, request, form, formsets, change):
        """Сохраняем связанные объекты (расписание)"""
        # Сначала сохраняем магазин
        super().save_related(request, form, formsets, change)

        # Для нового магазина проверяем, создалось ли расписание
        if not change:  # Если это создание нового магазина
            store = form.instance

            # Удаляем возможные дубликаты, созданные формой
            store.working_hours.all().delete()

            # Создаем правильное расписание на основе данных из формы
            for formset in formsets:
                if formset.model == WorkingHours:
                    instances = formset.save(commit=False)
                    for instance in instances:
                        # Проверяем, что это валидная запись (не пустая форма)
                        if instance.day_of_week is not None:
                            instance.store = store
                            instance.save()

    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).prefetch_related('working_hours')


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
admin.site.register(WorkingHours, WorkingHoursAdmin)