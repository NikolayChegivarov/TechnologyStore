from django.shortcuts import render
import json
from django.utils import timezone
from store_app.models import Store

def stores_view(request):
    # Упрощенная версия - получаем все города
    all_cities = Store.objects.values_list('city', flat=True).distinct().order_by('city')
    print(f"all_cities: {list(all_cities)}")  # Исправлено!

    # Фильтрация по городу
    selected_city = request.GET.get('city')

    if selected_city:
        stores = Store.objects.filter(city=selected_city).prefetch_related('working_hours')
    else:
        stores = Store.objects.all().prefetch_related('working_hours')

    # Подготавливаем данные для карты и шаблона
    stores_data = []
    for store in stores:
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

        is_open_now = store.is_open_now()

        stores_data.append({
            'id': store.id,
            'city': store.city,
            'address': store.address,
            'latitude': float(store.latitude) if store.latitude else None,
            'longitude': float(store.longitude) if store.longitude else None,
            'schedule': schedule,
            'is_open_now': is_open_now,
            'status_color': 'green' if is_open_now else 'red',
            'status_text': 'Открыт сейчас' if is_open_now else 'Закрыт'
        })

    stores_with_coords = [s for s in stores_data if s['latitude'] and s['longitude']]

    context = {
        'stores': stores_data,
        'stores_json': json.dumps(stores_with_coords, ensure_ascii=False),
        'cities': all_cities,
        'selected_city': selected_city,
        'total_stores': len(stores_data),
        'active_stores': len([s for s in stores_data if s['is_open_now']])
    }

    return render(request, 'basement/branches.html', context)