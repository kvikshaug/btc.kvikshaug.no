from django.db import models

class Price(models.Model):
    usdbtc = models.DecimalField(max_digits=14, decimal_places=8, null=True)
    usdnok = models.DecimalField(max_digits=12, decimal_places=8, null=True)
    rate_buy = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    rate_sell = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    def nokbtc(self):
        return Price.to_float(self.usdbtc) * Price.to_float(self.usdnok)

    def buy_price(self):
        return self.nokbtc() * self.buy_rate()

    def sell_price(self):
        return self.nokbtc() * self.sell_rate()

    def buy_rate(self):
        return self.rate_buy / 100.0

    def sell_rate(self):
        return self.rate_sell / 100.0

    @staticmethod
    def to_float(value):
        return value / 1000.0

    @staticmethod
    def to_int(value):
        return round(value * 1000)
