#!/usr/bin/python
from datetime import datetime
import decimal
import json
import logging
import logging.config
import signal
import sys

import pusherclient
import sqlalchemy

from . import settings
from .exceptions import Abort, Restart
from .exchangerate import ExchangeRate
from .models import Price

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)
Session = sqlalchemy.orm.sessionmaker()

class Ticker:
    BITSTAMP_APP_KEY = 'de504dc5763aeef9ff52'

    def __init__(self, *args, **kwargs):
        # Init db engine
        self.engine = sqlalchemy.create_engine(settings.DB_URL, echo=True)
        Session.configure(bind=self.engine)

        # Add signal handlers
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGHUP, self.handle_signal)

        # Initialize the exchange rate thread
        self.exchange_rate = ExchangeRate()

        logger.info("Connecting to the BitStamp websocket")
        self.pusher = pusherclient.Pusher(Ticker.BITSTAMP_APP_KEY, log_level=logging.WARNING)
        self.pusher.connection.bind('pusher:connection_established', self.subscribe)
        self.pusher.connect()

    def subscribe(self, data):
        logger.info("Pusher connection established, subscribing to trades")
        channel = self.pusher.subscribe('live_trades')
        channel.bind('trade', self.handle_trade)

    def handle_trade(self, data):
        session = Session()
        btcusd = json.loads(data, parse_float=decimal.Decimal)['price']
        usdnok = self.exchange_rate.get_rate()
        price = Price(btcusd=btcusd, usdnok=usdnok, datetime=datetime.now())
        session.add(price)
        session.commit()
        logger.debug("Saved new trade price: %s (USDNOK: %s)" % (btcusd, usdnok))

    def shutdown(self):
        logger.info("Closing sockets")
        self.pusher.disconnect()
        self.exchange_rate.stop()

    def handle_signal(self, signum, frame):
        logger.debug("Handling signal %s" % signum)
        if signum == signal.SIGTERM:
            raise Abort("Received SIGTERM")
        elif signum == signal.SIGHUP:
            raise Restart("Received SIGHUP")
        else:
            raise Exception("Never asked to handle signal %s" % signum)

def main():
    while True:
        try:
            ticker = Ticker()
            ticker.pusher.connection.join()
            logger.warning("Pusher connection exited unexpectedly; restarting")
        except (KeyboardInterrupt, Abort):
            logger.info("Received abort signal; shutting down")
            break
        except Restart:
            logger.info("Received restart signal; shutting down and restarting")
        except:
            logger.error("Unexpected exception; shutting down and restarting", exc_info=sys.exc_info())
        finally:
            ticker.shutdown()

if __name__ == "__main__":
    main()
