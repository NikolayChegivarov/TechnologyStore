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
            print("Аутентификация: username или password отсутствуют")
            return None

        print(f"Попытка аутентификации: username={username}, password={password}")

        try:
            # Пытаемся найти по username (для MANAGER / ADMIN) - ПЕРВЫМ!
            user = UserModel.objects.get(username=username)
            print(f"Найден пользователь по username: {user.username}, роль: {user.role}")

            if user.role != UserModel.Role.CUSTOMER:
                print("Пользователь не CUSTOMER - проверяем пароль")
                if user.check_password(password):
                    print("Пароль верный! Аутентификация успешна")
                    return user
                else:
                    print("Пароль неверный!")
            else:
                print("Пользователь CUSTOMER - пропускаем поиск по username")

        except UserModel.DoesNotExist:
            print(f"Пользователь с username '{username}' не найден")

        try:
            # Пытаемся найти по email (для CUSTOMERS) - только если email не пустой
            if username and '@' in username:  # проверяем, что это похоже на email
                print(f"Пытаемся найти по email: {username}")
                user = UserModel.objects.get(email=username)
                print(f"Найден пользователь по email: {user.username}, роль: {user.role}")

                if user.role == UserModel.Role.CUSTOMER:
                    print("Пользователь CUSTOMER - проверяем пароль")
                    if user.check_password(password):
                        print("Пароль верный! Аутентификация успешна")
                        return user
                    else:
                        print("Пароль неверный!")
                else:
                    print("Пользователь не CUSTOMER - пропускаем поиск по email")
            else:
                print("Username не похож на email - пропускаем поиск по email")

        except UserModel.DoesNotExist:
            print(f"Пользователь с email '{username}' не найден")

        print("Аутентификация не удалась")
        return None
