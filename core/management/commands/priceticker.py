import decimal
import json
import logging
import signal

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand

import pusherclient
import raven

from core.models import CurrentRate, Price

from core.management.commands.ticker.exceptions import Abort, Restart
from core.management.commands.ticker.exchangerate import ExchangeRate

logger = logging.getLogger('btc.priceticker')
raven_client = raven.Client(settings.RAVEN_CONFIG['dsn'])

class Command(BaseCommand):
    help = 'Run the price ticker'

    def handle(self, *args, **options):
        while True:
            try:
                ticker = Ticker()
                ticker.pusher.connection.join()
                logger.warning("Pusher connection exited unexpectedly; restarting...")
            except (KeyboardInterrupt, Abort):
                logger.info("Received abort signal; shutting down...")
                break
            except Restart:
                logger.info("Received restart signal; shutting down and restarting...")
            except Exception as e:
                raven_client.captureException()
                logger.error("Unexpected exception: %s" % e)
                logger.info("Shutting down and restarting...")
            finally:
                ticker.shutdown()

class Ticker:
    BITSTAMP_APP_KEY = 'de504dc5763aeef9ff52'

    def __init__(self, *args, **kwargs):
        # Add signal handlers
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGHUP, self.handle_signal)

        # Initialize the exchange rate thread
        self.exchange_rate = ExchangeRate()

        logger.info("Connecting to the BitStamp websocket...")
        self.pusher = pusherclient.Pusher(Ticker.BITSTAMP_APP_KEY)
        self.pusher.connection.bind('pusher:connection_established', self.subscribe)
        self.pusher.connect()
        self.price = None

    def subscribe(self, data):
        logger.info("Pusher connection established, subscribing to trades...")
        channel = self.pusher.subscribe('live_trades')
        channel.bind('trade', self.handle_trade)

    def handle_trade(self, data):
        new_price = json.loads(data, parse_float=decimal.Decimal)['price']
        current_rate = CurrentRate.objects.get()
        price = Price(
            usdbtc=new_price,
            usdnok=self.exchange_rate.get_rate(),
            buy_rate=current_rate.buy_rate,
            sell_rate=current_rate.sell_rate,
        )
        price.save()
        cache.set('price.last', price, Price.LAST_PRICE_CACHE_PERIOD)
        logger.debug("Saved new trade price: %s (USDNOK: %s, buy rate: %s, sell rate: %s)" % (
            price.usdbtc,
            price.usdnok,
            price.buy_rate,
            price.sell_rate,
        ))

    def calculate_price(self):
        rate = self.exchange_rate.get_rate()
        if self.price is None:
            logger.warning("Asked to calculate price, but no trade has been recorded yet; returning None")
            return None
        elif rate is None:
            logger.warning("Asked to calculate price, but the exchange rate hasn't been fetched yet; returning None")
            return None
        else:
            nok_price = self.price * rate
            logger.debug("Current price: kr %s (USD: %s, USDNOK rate: %s)" % (nok_price, self.price, rate))
            return nok_price

    def shutdown(self):
        logger.info("Closing sockets...")
        self.pusher.disconnect()
        self.exchange_rate.stop()

    def handle_signal(self, signum, frame):
        logger.debug("Handling signal %s" % signum)
        if signum == signal.SIGTERM:
            raise Abort("Received SIGTERM; shutting down...")
        elif signum == signal.SIGHUP:
            raise Restart("Received SIGHUP; restarting...")
        else:
            raise Exception("Never asked to handle signal %s" % signum)
