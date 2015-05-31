from django.db import models

class Price(models.Model):
    price = models.PositiveIntegerField()
    datetime = models.DateTimeField(auto_now_add=True)

    @property
    def price_float(self):
        return self.price / 1000.0

    @price_float.setter
    def price_float(self, price):
        self.price = round(price * 1000)
