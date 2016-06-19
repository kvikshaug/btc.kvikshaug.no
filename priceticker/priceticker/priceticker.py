#!/usr/bin/python
from datetime import datetime
import logging
import logging.config
import signal
import threading

import sqlalchemy

from . import settings
from .workers import USDNOKWorker, BTCUSDWorker, DBCleaner
from .models import Price

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)
Session = sqlalchemy.orm.sessionmaker()

class Ticker:
    def __init__(self, *args, **kwargs):
        logger.debug("Creating database engine")
        self.engine = sqlalchemy.create_engine(settings.DB_URL)
        Session.configure(bind=self.engine)

        logger.debug("Starting USDNOK worker")
        self.usdnok_first = threading.Event()
        self.usdnok_lock = threading.Lock()
        self.usdnok_worker = USDNOKWorker(self)
        logger.info("Waiting for first usdnok price")
        self.usdnok_first.wait()

        logger.debug("Starting BTCUSD worker")
        self.btcusd_worker = BTCUSDWorker(self)

        logger.debug("Starting DB cleaner")
        self.db_cleaner = DBCleaner(self, Session)

    def set_usdnok(self, usdnok):
        with self.usdnok_lock:
            self.usdnok = usdnok
            self.usdnok_first.set()

    def set_btcusd(self, btcusd):
        with self.usdnok_lock:
            usdnok = self.usdnok
        session = Session()
        price = Price(btcusd=btcusd, usdnok=usdnok, datetime=datetime.now())
        session.add(price)
        session.commit()
        logger.info("Saved new trade price: %s" % price)
        session.close()

    def run_forever(self):
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
        signal.pause()

    def shutdown(self, signum, frame):
        logger.info("Received signal %s, stopping workers" % signum)
        self.usdnok_worker.stop()
        self.btcusd_worker.stop()
        self.db_cleaner.stop()

def main():
    ticker = Ticker()
    ticker.run_forever()

if __name__ == "__main__":
    main()
