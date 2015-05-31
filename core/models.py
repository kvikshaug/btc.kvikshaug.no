from django.db import models

class Price(models.Model):
    usdbtc = models.PositiveIntegerField()
    usdnok = models.PositiveIntegerField()
    rate_buy = models.PositiveIntegerField()
    rate_sell = models.PositiveIntegerField()
    datetime = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def to_float(value):
        return value / 1000.0

    @staticmethod
    def to_int(value):
        return round(value * 1000)
