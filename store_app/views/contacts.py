from django.shortcuts import render
from ..models import Store, WorkingHours
import json
from django.utils import timezone
from collections import defaultdict


def branches_view(request):
    """
    Представление для отображения филиалов
    """
    try:
        # Получаем все активные магазины
        stores = Store.objects.filter(is_active=True).prefetch_related('working_hours')
        active_stores_count = stores.count()

        # Если нет активных магазинов
        if active_stores_count == 0:
            context = {
                'cities': [],
                'cities_json': json.dumps([], ensure_ascii=False),
                'total_branches': 0,
                'active_branches': 0,
            }
            return render(request, 'basement/branches.html', context)

        # Группируем магазины по городам
        cities_dict = defaultdict(list)

        for store in stores:
            # Получаем расписание для каждого магазина
            schedule = []
            working_hours = store.working_hours.all().order_by('day_of_week')

            for wh in working_hours:
                if wh.is_closed:
                    time_str = "Выходной"
                else:
                    open_time = wh.opening_time.strftime('%H:%M') if wh.opening_time else '--:--'
                    close_time = wh.closing_time.strftime('%H:%M') if wh.closing_time else '--:--'
                    time_str = f"{open_time} - {close_time}"

                schedule.append({
                    'day': wh.get_day_of_week_display(),
                    'time': time_str,
                    'is_closed': wh.is_closed
                })

            # Проверяем, открыт ли магазин сейчас
            is_open_now = store.is_open_now()

            # ВАЖНО: Проверяем корректность координат
            latitude = None
            longitude = None

            if store.latitude and store.longitude:
                try:
                    lat_val = float(store.latitude)
                    lng_val = float(store.longitude)
                    # Проверяем, что координаты в разумных пределах для России
                    if 40.0 <= lng_val <= 180.0 and 30.0 <= lat_val <= 80.0:
                        latitude = lat_val
                        longitude = lng_val
                    else:
                        print(f"Некорректные координаты для магазина {store.id}: {lat_val}, {lng_val}")
                except (ValueError, TypeError) as e:
                    print(f"Ошибка преобразования координат для магазина {store.id}: {e}")

            store_data = {
                'id': store.id,
                'city': store.city,
                'address': store.address,
                'phone': store.phone or 'Не указан',
                'description': store.description,
                'latitude': latitude,
                'longitude': longitude,
                'schedule': schedule,
                'is_open_now': is_open_now,
                'status_color': 'green' if is_open_now else 'red',
                'status_text': 'Открыт' if is_open_now else 'Закрыт'
            }

            cities_dict[store.city].append(store_data)

        # Формируем данные для городов
        cities_data = []
        for city, city_stores in cities_dict.items():
            # Фильтруем только магазины с корректными координатами
            branches_with_coords = [b for b in city_stores if b['latitude'] and b['longitude']]

            cities_data.append({
                'city': city,
                'branch_count': len(city_stores),
                'branches': city_stores,
                'branches_with_coords': branches_with_coords
            })

        # Сортируем города по алфавиту
        cities_data.sort(key=lambda x: x['city'])

        # Данные для JSON (только магазины с координатами)
        cities_json_data = []
        for city_data in cities_data:
            if city_data['branches_with_coords']:
                cities_json_data.append({
                    'city': city_data['city'],
                    'branches': city_data['branches_with_coords']
                })

        # Подготовка контекста
        total_branches = len(stores)
        active_branches = len([s for s in stores if s.is_open_now()])

        context = {
            'cities': cities_data,
            'cities_json': json.dumps(cities_json_data, ensure_ascii=False),
            'total_branches': total_branches,
            'active_branches': active_branches,
        }

    except Exception as e:
        print(f"Ошибка в branches_view: {e}")
        context = {
            'cities': [],
            'cities_json': json.dumps([], ensure_ascii=False),
            'total_branches': 0,
            'active_branches': 0,
        }

    return render(request, 'basement/branches.html', context)