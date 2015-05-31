from django.db import models

class Price(models.Model):
    usdbtc = models.DecimalField(max_digits=14, decimal_places=8, null=True)
    usdnok = models.DecimalField(max_digits=12, decimal_places=8, null=True)
    rate_buy = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    rate_sell = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    @property
    def nokbtc(self):
        return self.usdbtc * self.usdnok

    @property
    def buy_price(self):
        return self.nokbtc * self.rate_buy

    @property
    def sell_price(self):
        return self.nokbtc * self.rate_sell
