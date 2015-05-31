import json
import logging
import socket
import signal

from django.conf import settings
from django.core.management.base import BaseCommand

import pusherclient
import raven

from core.management.commands.ticker.exceptions import Abort, Restart
from core.management.commands.ticker.exchangerate import ExchangeRate

logger = logging.getLogger(__name__)
raven_client = raven.Client(settings.SENTRY_DSN)

class Command(BaseCommand):
    help = 'Run the price ticker'

    def handle(self, *args, **options):
        while True:
            try:
                ticker = Ticker()
                ticker.listen()
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
    LISTEN_PORT = 7139

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
        self.price = json.loads(data)['price']
        logger.debug("Received new trade price: %s" % self.price)

    def listen(self):
        """Send the current price as a JSON value (number) to incoming connections"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', Ticker.LISTEN_PORT))
        self.socket.listen(5)
        logger.info("Listening on 0.0.0.0:%s" % Ticker.LISTEN_PORT)
        while True:
            client, address = self.socket.accept()
            logger.debug("Accepted connection, calculating price...")
            price = self.calculate_price()
            bytes = json.dumps(price).encode('utf-8')
            client.send(bytes)
            client.close()

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
        try:
            self.socket.shutdown(socket.SHUT_WR)
        except:
            logger.warning("Unable to shutdown listener socket; ignoring and closing it...")
        self.socket.close()
        self.exchange_rate.stop()

    def handle_signal(self, signum, frame):
        logger.debug("Handling signal %s" % signum)
        if signum == signal.SIGTERM:
            raise Abort("Received SIGTERM; shutting down...")
        elif signum == signal.SIGHUP:
            raise Restart("Received SIGHUP; restarting...")
        else:
            raise Exception("Never asked to handle signal %s" % signum)
