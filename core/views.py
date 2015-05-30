from django.shortcuts import render

from core import price

def index(request):
    context = {
        'price': price.get_current(),
    }
    return render(request, 'core/index.html', context)
