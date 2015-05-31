from datetime import timedelta
import json

from django.conf import settings
from django.shortcuts import render
from django.utils import timezone

from core.models import Price

def index(request):
    one_day_ago = timezone.now() - timedelta(days=1)
    prices = Price.objects.filter(datetime__gte=one_day_ago).order_by('datetime')

    price_history = [
        ['Tid', 'Kjøp', 'Salg'],
    ]

    prev_buy = None
    prev_sell = None
    date_point = one_day_ago
    for price in prices:
        while price.datetime > date_point:
            price_history.append([
                date_point.strftime("%H:%M"),
                prev_buy,
                prev_sell,
            ])
            date_point += timedelta(minutes=settings.CHART_GRANULARITY)
        prev_buy = float(round(price.buy_price, 2))
        prev_sell = float(round(price.sell_price, 2))

    context = {
        'price': Price.objects.order_by('datetime')[:1][0],
        'price_history': json.dumps(price_history),
    }
    return render(request, 'core/index.html', context)
