from django.core.cache import cache
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save

class CurrentRate(models.Model):
    buy_rate = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    sell_rate = models.DecimalField(max_digits=3, decimal_places=2, null=True)

class Price(models.Model):
    LAST_PRICE_CACHE_PERIOD = 60 * 60

    usdbtc = models.DecimalField(max_digits=14, decimal_places=8, null=True)
    usdnok = models.DecimalField(max_digits=12, decimal_places=8, null=True)
    buy_rate = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    sell_rate = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s: kr %s @ %s' % (self.pk, self.nokbtc, self.datetime)

    @property
    def nokbtc(self):
        return self.usdbtc * self.usdnok

    @property
    def buy_price(self):
        return self.nokbtc * self.buy_rate

    @property
    def sell_price(self):
        return self.nokbtc * self.sell_rate

@receiver(post_save, sender=Price)
def cache_last_price(sender, instance, created, **kwargs):
    if created:
        cache.set('price.last', instance, Price.LAST_PRICE_CACHE_PERIOD)
