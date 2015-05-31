import logging
import threading

import requests

logger = logging.getLogger(__name__)

class ExchangeRate(threading.Thread):
    YAHOO_FINANCE_URL = "https://download.finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&s=USDNOK=X"
    YAHOO_FINANCE_PARAMS = {'e': '.csv', 'f': 'sl1d1t1', 's': 'USDNOK=X'}
    SLEEP_TIME = 60 * 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate = None
        self.stop_event = threading.Event()
        self.start()

    def get_rate(self):
        return self.rate

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            try:
                logger.debug("Fetching exchange rates from Yahoo Finance...")
                csv = requests.get(ExchangeRate.YAHOO_FINANCE_URL, params=ExchangeRate.YAHOO_FINANCE_PARAMS).text
                name, rate, date, time = csv.split(',')
                self.rate = float(rate)
                self.stop_event.wait(ExchangeRate.SLEEP_TIME)
            except Exception as e:
                logger.warning("Unhandled exception: %s" % e)
                logger.warning("Ignoring and trying to re-fetch exchange rate...")
