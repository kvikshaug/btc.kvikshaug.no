import decimal
from pytz import timezone

# Project settings: active buy/sell rates
BUY_RATE = decimal.Decimal("0.99")
SELL_RATE = decimal.Decimal("1.02")

TIMEZONE = timezone('Europe/Oslo')
