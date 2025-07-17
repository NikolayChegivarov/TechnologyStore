from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class RoleBasedAuthBackend(ModelBackend):
    """
    Кастомный бэкенд аутентификации, который различает способы входа для разных ролей:

    Для CUSTOMER - проверяет email и пароль

    Для MANAGER/ADMIN - проверяет username и пароль
    Если пользователь не найден или пароль неверный, возвращает None
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            # Пытаемся найти по email (для CUSTOMERS)
            user = UserModel.objects.get(email=username)
            if user.role == UserModel.Role.CUSTOMER and user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            pass

        try:
            # Пытаемся найти по username (для MANAGER / ADMIN)
            user = UserModel.objects.get(username=username)
            if user.role != UserModel.Role.CUSTOMER and user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            pass

        return None
