from itertools import groupby
from datetime import datetime, timedelta

from cache import cache
from database import db_session
from models import Price

CHART_GRANULARITY = 3 # Minutes between price measurements

def get_price_history(app):
    now = datetime.now()
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

    # Include an extra hour, which might be fetched by cache or query, in order to make sure the price *previous to the
    # very first one in the chart* is included. If it weren't, that data point would be null, since price history would
    # by definition start *after* that data point. If the case is that no trades have happened in that hour, the data
    # point will still be null (and further ones after that until a trade has happened).
    one_hour_before_date_point = date_point - timedelta(hours=1)

    # Now retrieve as many cached query results as possible, before selecting the remainder
    query_start_date = one_hour_before_date_point
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
    remaining_prices = db_session.query(Price).filter(
        Price.datetime >= query_start_date,
        Price.datetime <= now,
    ).order_by(Price.datetime)
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
                60 * 60 * 25, # Note that we're caching for 25 hours since we'll be quering 25 hours back
            )

    # Now that we've retrieved or queried all prices, there should be some extra ones from the hour *before* 24h ago.
    # Find the latest one of them (if any), and set that one as the previous price
    previous_price = None
    prices_before_chart_start = [p for p in prices if p.datetime < date_point]
    if len(prices_before_chart_start) > 0:
        previous_price = prices_before_chart_start[-1]

    # Finally group the prices by date and hour, so we can easily calculate plot points per hour
    prices_by_hour = {}
    for group, price_group in groupby(prices, key=lambda p: p.datetime.strftime("%d.%H:00")):
        prices_by_hour[group] = list(price_group)

    # Now iterate each hour, calculate the prices for each of them and cache most of the results, except for the very
    # last hour - we'll want to recalculate that with new trade data each request until a complete hour history has
    # been recorded. After caching we'll remove prices older than 24h ago, so that the chart plots exactly 24h at any
    # time.
    twentyfour_hours_ago = now - timedelta(hours=24)
    while date_point < one_hour_ago:
        hour_set = cache.get('price.history.result.by_hour.%s' % date_point.strftime("%d.%m.%Y.%H:%M"))
        if hour_set is None:
            try:
                prices_this_hour = prices_by_hour[date_point.strftime("%d.%H:00")]
            except KeyError:
                # Probably won't occur here unless
                # a) there's a serious issue with the stock exchange, or
                # b) our ticker has stopped for over an hour
                prices_this_hour = []
            hour_set = _calculate_hour(app, date_point, now, previous_price, prices_this_hour)
            cache.set('price.history.result.by_hour.%s' % date_point.strftime("%d.%m.%Y.%H:%M"), hour_set, 60 * 60 * 24)
        hour_history, previous_price = hour_set

        # Remove results older than 24h ago, now that they're cached
        if date_point < twentyfour_hours_ago:
            hour_history_within_24h = []
            for h in hour_history:
                _, minute = h[0].split(":")
                if int(minute) >= now.minute:
                    hour_history_within_24h.append(h)
            hour_history = hour_history_within_24h

        price_history.extend(hour_history)
        date_point += timedelta(hours=1)

    # We're at the last hour; calculate that without caching it
    try:
        prices_this_hour = prices_by_hour[date_point.strftime("%d.%H:00")]
    except KeyError:
        # Might occur at the start of a new hour when no trades have been recorded
        prices_this_hour = []
    hour_set = _calculate_hour(app, date_point, now, previous_price, prices_this_hour)
    hour_history, previous_price = hour_set
    price_history.extend(hour_history)
    return price_history

def _calculate_hour(app, date_point, now, previous_price, prices):
    """
    Calculates a list of plot points with applicable prices for one hour.
    - date_point: The datetime to begin calculations at; the start of an hour
    - now: The current datetime; passed as reference to avoid skew during code execution
    - previous_price: The applicable price *before* the current date_point start, may be None if unknown
    - prices: A list of trade prices for the applicable hour
    """
    an_hour_from_datepoint = date_point + timedelta(hours=1)

    price_index = 0
    price_count = len(prices)
    hour_history = []
    previous_date_point = date_point - timedelta(minutes=CHART_GRANULARITY)

    # Iterate while we're within the hour, and while we're not in the future (latter case applies for the final hour
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
            buy_price = float(round(previous_price.btcnok(rate=app.config['BUY_RATE']), 2))
            sell_price = float(round(previous_price.btcnok(rate=app.config['SELL_RATE']), 2))

        hour_history.append([
            app.config['TIMEZONE'].fromutc(date_point).strftime("%H:%M"),
            # timezone.localtime(date_point).strftime("%H:%M"),
            buy_price,
            sell_price,
        ])

        previous_date_point = date_point
        date_point += timedelta(minutes=CHART_GRANULARITY)
    return hour_history, previous_price
