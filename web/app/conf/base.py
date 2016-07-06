import decimal
import os
from pytz import timezone

# Project settings: active buy/sell rates
BUY_RATE = decimal.Decimal(os.environ['BUY_RATE'])
SELL_RATE = decimal.Decimal(os.environ['SELL_RATE'])

TIMEZONE = timezone('Europe/Oslo')
