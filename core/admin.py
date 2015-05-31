from django.contrib import admin

from .models import CurrentRate, Price

admin.site.register(CurrentRate)
admin.site.register(Price)
