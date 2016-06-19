from sqlalchemy import Column, Integer, Numeric, DateTime

from database import Base

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
