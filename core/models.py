from django.db import models

class Price(models.Model):
    price = models.PositiveIntegerField()
    datetime = models.DateTimeField()
