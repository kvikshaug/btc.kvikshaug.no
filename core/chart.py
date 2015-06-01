from itertools import groupby
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from core.models import Price

def get_price_history():
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(days=1)

    price_history = [
        ['Tid', 'Kjøp', 'Salg'],
    ]

    # The date point begins at the start of the chart and will increment with the chart granularity
    date_point = one_day_ago

    # Let's always start the chart at *the start of* an hour. This'll make caching easier
    date_point -= timedelta(
        minutes=date_point.minute,
        seconds=date_point.second,
        microseconds=date_point.microsecond,
    )

    previous_date_point = date_point - timedelta(minutes=settings.CHART_GRANULARITY)
    previous_price = None
    price_index = 0

    # Retrieve as many cached query results as possible, before selecting the remainder
    query_start_date = date_point
    prices = []
    while True:
        price_hour = cache.get('price.history.query.by_hour.%s' % query_start_date.strftime("%d.%m.%Y.%H:%M"))
        if price_hour is None:
            # End of cache; stop
            break
        elif query_start_date >= one_hour_ago:
            # Cached up to an hour ago? We don't want that; stop
            break
        else:
            prices.extend(price_hour)
            query_start_date += timedelta(hours=1)

    # Select *remaining* prices and cache them by the hour
    # Note that this query actually is quite heavy on the CPU because of decimal conversions
    remaining_prices = Price.objects.filter(datetime__gte=query_start_date, datetime__lte=now).order_by('datetime')
    prices.extend(remaining_prices)
    for hour, hour_prices in groupby(remaining_prices, key=lambda p: p.datetime.strftime("%H:00")):
        # Cache by hour, up until, but not including, the last hour
        hour_prices = list(hour_prices)
        if hour_prices[0].datetime < one_hour_ago:
            cache.set(
                'price.history.query.by_hour.%s' % (
                    hour_prices[0].datetime.strftime("%d.%m.%Y.%H:00")
                ),
                hour_prices,
                60 * 60 * 24,
            )

    while date_point < one_hour_ago:
        hour_set = cache.get('price.history.result.by_hour.%s' % date_point.strftime("%d.%m.%Y.%H:%M"))
        if hour_set is None:
            hour_set = _calculate_hour(previous_date_point, date_point, prices, price_index, previous_price, now)
            cache.set('price.history.result.by_hour.%s' % date_point.strftime("%d.%m.%Y.%H:%M"), hour_set, 60 * 60 * 24)
        hour_history, price_index, previous_price = hour_set
        price_history.extend(hour_history)
        date_point += timedelta(hours=1)

    # We're at the last hour; calculate that without caching it
    hour_set = _calculate_hour(previous_date_point, date_point, prices, price_index, previous_price, now)
    hour_history, price_index, previous_price = hour_set
    price_history.extend(hour_history)
    return price_history

def _calculate_hour(previous_date_point, date_point, prices, price_index, previous_price, now):
    an_hour_from_datepoint = date_point + timedelta(hours=1)

    price_count = len(prices)
    hour_history = []

    # Iterate while we're within the our, and while we're not in the future (latter case applies for the final hour
    # calculation)
    while date_point <= an_hour_from_datepoint and date_point <= now:
        # Find the latest price within the granularity range. Keep an index in order to iterate the prices along with
        # the date ranges.
        while price_index < price_count:
            price = prices[price_index]
            if price.datetime < previous_date_point:
                # This price is *before* this date point range; ignore it and check the next one
                price_index += 1
                continue
            elif price.datetime >= previous_date_point and price.datetime <= date_point:
                # This price is within our range, set it as relevant
                previous_price = price

                # Iterate to see if next price might be relevant too
                price_index += 1
                continue
            elif price.datetime > date_point:
                # Nope, this price is actually after the current date point; stop iterating, we'll check it again next
                # date point
                break
            else:
                raise Exception("This should never *ever* happen")

        if previous_price is None:
            # This might be the case if it's an early range and there hasn't been any price recorded yet
            buy_price = None
            sell_price = None
        else:
            # The relevant price will now either be leftover from a previous range or a new relevant one
            buy_price = float(round(previous_price.buy_price, 2))
            sell_price = float(round(previous_price.sell_price, 2))

        hour_history.append([
            date_point.strftime("%H:%M"),
            buy_price,
            sell_price,
        ])

        previous_date_point = date_point
        date_point += timedelta(minutes=settings.CHART_GRANULARITY)
    return hour_history, price_index, previous_price
