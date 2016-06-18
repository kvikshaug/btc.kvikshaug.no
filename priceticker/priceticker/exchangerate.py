import decimal
import logging
import sys
import threading

import requests

logger = logging.getLogger(__name__)

class ExchangeRate(threading.Thread):
    YAHOO_FINANCE_URL = "https://download.finance.yahoo.com/d/quotes.csv"
    YAHOO_FINANCE_PARAMS = {'e': '.csv', 'f': 'sl1d1t1', 's': 'USDNOK=X'}
    UPDATE_RATE = 60 * 10 # seconds

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
                logger.info("Fetching exchange rates from Yahoo Finance")
                csv = requests.get(ExchangeRate.YAHOO_FINANCE_URL, params=ExchangeRate.YAHOO_FINANCE_PARAMS).text
                name, rate, date, time = csv.split(',')
                self.rate = decimal.Decimal(rate)
                self.stop_event.wait(ExchangeRate.UPDATE_RATE)
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
