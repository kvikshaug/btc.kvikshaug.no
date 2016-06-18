from sqlalchemy import Column, Integer, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True)
    btcusd = Column(Numeric(precision=14, scale=8), nullable=True)
    usdnok = Column(Numeric(precision=12, scale=8), nullable=True)
    datetime = Column(DateTime)

    def __repr__(self):
        return "<Price(btcusd='%s', usdnok='%s', datetime='%s')>" % (
            self.btcusd,
            self.usdnok,
            self.datetime,
        )
