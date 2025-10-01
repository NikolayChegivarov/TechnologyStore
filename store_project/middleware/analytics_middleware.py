import time
from django.utils import timezone
from store_app.models import PageView


class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Время начала обработки запроса
        start_time = time.time()

        # Получаем ответ
        response = self.get_response(request)

        # Время окончания обработки
        duration = time.time() - start_time

        # Игнорируем статические файлы и админку
        if not any(path in request.path for path in ['/static/', '/media/', '/admin/']):
            self.track_page_view(request, duration)

        return response

    def track_page_view(self, request, duration):
        """Сохраняет информацию о просмотре страницы"""
        try:
            PageView.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key or 'anonymous',
                url=request.path,
                referer=request.META.get('HTTP_REFERER'),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                duration=int(duration)
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем выполнение
            print(f"Error tracking page view: {e}")

    def get_client_ip(self, request):
        """Получает реальный IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip