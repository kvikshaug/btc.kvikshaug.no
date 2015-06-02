from datetime import timedelta
import logging

from django.core.cache import cache
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

logger = logging.getLogger('btc.core')

class CurrentRate(models.Model):
    buy_rate = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    sell_rate = models.DecimalField(max_digits=3, decimal_places=2, null=True)

class Price(models.Model):
    LAST_PRICE_CACHE_PERIOD = 60 * 60
    LAST_PRICE_ACCEPTABLE_AGE = 60 * 15

    btcusd = models.DecimalField(max_digits=14, decimal_places=8, null=True)
    usdnok = models.DecimalField(max_digits=12, decimal_places=8, null=True)
    buy_rate = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    sell_rate = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s: kr %s @ %s' % (self.pk, round(self.nokbtc, 2), self.datetime)

    @property
    def nokbtc(self):
        return self.btcusd * self.usdnok

    @property
    def buy_price(self):
        return self.nokbtc * self.buy_rate

    @property
    def sell_price(self):
        return self.nokbtc * self.sell_rate

    @staticmethod
    def last_price():
        price = cache.get('price.last')
        if price is None:
            price = Price.objects.order_by('-datetime')[:1][0]
            cache.set('price.last', price, Price.LAST_PRICE_CACHE_PERIOD)

        # Check that the last price isn't too old. It might be possible that there just hasn't been any trades for
        # this period, but in the worst case, our priceticker might have stopped.
        # You could potentially consider explicitly pulling the latest price from the BitStamp API here.
        if price.datetime + timedelta(seconds=Price.LAST_PRICE_ACCEPTABLE_AGE) < timezone.now():
            logger.warning("Last price is older than the acceptable age!",
                extra={
                    'price': price,
                    'now': timezone.now(),
                }
            )

        return price

    class Meta:
        ordering = ['-datetime']

@receiver(post_save, sender=Price)
def cache_last_price(sender, instance, created, **kwargs):
    if created:
        logger.debug("Caching newly created price object as last price: %s" % instance)
        cache.set('price.last', instance, Price.LAST_PRICE_CACHE_PERIOD)
