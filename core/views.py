from django.shortcuts import render

from core.models import Price

def index(request):
    context = {
        'price': Price.objects.order_by('datetime')[:1][0],
    }
    return render(request, 'core/index.html', context)
