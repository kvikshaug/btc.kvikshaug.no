import logging

from sqlalchemy import Column, Integer, Numeric, DateTime

from database import Base, db_session
from datetime import datetime, timedelta
from conf import settings

logger = logging.getLogger(__name__)

class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True)
    btcusd = Column(Numeric(precision=14, scale=8))
    usdnok = Column(Numeric(precision=12, scale=8))
    datetime = Column(DateTime)

    def __repr__(self):
        return "<Price(btcusd='%s', usdnok='%s', datetime='%s')>" % (
            self.btcusd,
            self.usdnok,
            self.datetime,
        )

    def btcnok(self, rate=1):
        return self.btcusd * self.usdnok * rate

    @staticmethod
    def last():
        last_price = db_session.query(Price).order_by(Price.datetime.desc()).first()
        if last_price is None:
            return None

        # Check the age of the last price. If it's too old, there might not have been any trades for a while, or more
        # likely; the priceticker has stopped.
        now = settings['TIMEZONE'].fromutc(datetime.utcnow())
        acceptable_age = timedelta(minutes=15)
        if settings['TIMEZONE'].fromutc(last_price.datetime) + acceptable_age < now:
            logger.warning(
                "Last trade price is too old",
                extra={'last_price': last_price, 'now': now},
            )

        return last_price
