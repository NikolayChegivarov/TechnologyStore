from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Manager, Store


class StoreAdmin(admin.ModelAdmin):
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
    определяет отображаемые поля в списке пользователей, группирует поля по разделам
    (учётные данные, персональные данные, права доступа, даты), добавляет подсказки к полям.
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
        """Дублирует созданного пользователя в объект MANAGER"""
        # При сохранении суперпользователя устанавливаем роль ADMIN
        if obj.is_superuser:
            obj.role = User.Role.ADMIN

        super().save_model(request, obj, form, change)

        # Создаем или обновляем профиль менеджера при необходимости
        if obj.role == User.Role.MANAGER:
            if obj.manager_profile:
                # Обновляем существующий профиль менеджера
                manager = obj.manager_profile
                manager.first_name = obj.first_name
                manager.last_name = obj.last_name
                manager.save()
            else:
                # Создаем новый профиль менеджера
                manager = Manager.objects.create(
                    first_name=obj.first_name,
                    last_name=obj.last_name,
                    phone='',  # можно установить значение по умолчанию
                    position='Менеджер',  # или оставить пустым
                    is_active=True
                )
                obj.manager_profile = manager
                obj.save()

admin.site.register(Store, StoreAdmin)
admin.site.register(User, CustomUserAdmin)
