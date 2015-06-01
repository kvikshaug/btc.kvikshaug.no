import json

from django.shortcuts import render

from core.chart import get_price_history
from core.models import Price

def index(request):
    context = {
        'price': Price.last_price(),
        'price_history': json.dumps(get_price_history()),
    }
    return render(request, 'core/index.html', context)
