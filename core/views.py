from django.conf import settings
from django.shortcuts import render

from core.models import Price

def index(request):
    price = Price.objects.order_by('datetime')[:1][0]
    buy = price.price_float * settings.BUY_RATE
    sell = price.price_float * settings.SELL_RATE
    price = {
        'buy': buy,
        'sell': sell,
    }
    context = {
        'price': price,
    }
    return render(request, 'core/index.html', context)
