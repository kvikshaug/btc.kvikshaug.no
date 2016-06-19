from datetime import datetime, timedelta
import decimal
import json
import logging
import sys
import threading

import pusherclient
import requests

from .models import Price

logger = logging.getLogger(__name__)

class USDNOKWorker(threading.Thread):
    """Retrieve USD/NOK rate from Yahoo Finance and send back to the Ticker"""
    YAHOO_FINANCE_URL = "https://download.finance.yahoo.com/d/quotes.csv"
    YAHOO_FINANCE_PARAMS = {'e': '.csv', 'f': 'sl1d1t1', 's': 'USDNOK=X'}
    UPDATE_RATE = 60 * 10 # seconds

    def __init__(self, ticker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticker = ticker
        self.stop_event = threading.Event()
        self.start()

    def run(self):
        while not self.stop_event.is_set():
            try:
                logger.debug("Fetching exchange rates from Yahoo Finance")
                csv = requests.get(USDNOKWorker.YAHOO_FINANCE_URL, params=USDNOKWorker.YAHOO_FINANCE_PARAMS).text
                name, rate, date, time = csv.split(',')
                usdnok = decimal.Decimal(rate)
                logger.debug("New USDNOK rate: %s" % usdnok)
                self.ticker.set_usdnok(usdnok)
                self.stop_event.wait(USDNOKWorker.UPDATE_RATE)
            except:
                # Likely a problem with Yahoo's service; log a warning and retry
                # Try to include the response text in the log data if it is available
                try:
                    extra = {'response': csv}
                except NameError:
                    extra = {}

                logger.warning(
                    "Couldn't look up USD/NOK exchange rate; ignoring and re-fetching instantly",
                    exc_info=sys.exc_info(),
                    extra=extra,
                )

    def stop(self):
        logger.debug("USDNOKWorker: Stopping")
        self.stop_event.set()

class BTCUSDWorker:
    """Retrieve BTC/USD rate from Bitstamp API and send back to the Ticker"""
    BITSTAMP_APP_KEY = 'de504dc5763aeef9ff52'

    def __init__(self, ticker, *args, **kwargs):
        self.ticker = ticker
        self.pusher = pusherclient.Pusher(BTCUSDWorker.BITSTAMP_APP_KEY, log_level=logging.WARNING)
        self.pusher.connection.bind('pusher:connection_established', self.subscribe)
        self.pusher.connect()

    def subscribe(self, data):
        logger.debug("BTCUSDWorker: Pusher connection established, subscribing to trades")
        channel = self.pusher.subscribe('live_trades')
        channel.bind('trade', self.handle_trade)

    def handle_trade(self, data):
        btcusd = json.loads(data, parse_float=decimal.Decimal)['price']
        logger.debug("New BTCUSD rate: %s" % btcusd)
        self.ticker.set_btcusd(btcusd)

    def stop(self):
        logger.debug("BTCUSDWorker: Disconnecting from Pusher")
        self.pusher.disconnect()

class DBCleaner(threading.Thread):
    """Purge old price history"""
    HISTORY = timedelta(days=3)
    CLEANING_RATE = 60 * 60 * 24 # seconds

    def __init__(self, ticker, Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticker = ticker
        self.Session = Session
        self.stop_event = threading.Event()
        self.start()

    def run(self):
        while not self.stop_event.is_set():
            session = self.Session()
            date_limit = datetime.now() - DBCleaner.HISTORY
            logger.debug("DBCleaner: Purging prices from before %s" % date_limit)
            count = session.query(Price).filter(Price.datetime < date_limit).delete()
            session.commit()
            session.close()
            logger.debug("DBCleaner: Deleted %s price objects" % count)
            self.stop_event.wait(DBCleaner.CLEANING_RATE)

    def stop(self):
        logger.debug("DBCleaner: Stopping")
        self.stop_event.set()
