from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from core.models import Price

def get_price_history():
    now = timezone.now()
    one_day_ago = now - timedelta(days=1)

    # We might need to include price objects from *CHART_GRANULARITY* minutes before the point 24h ago
    # That's a bit arbitrary; a trade price *could* be from even before the granularity + 24h ago and still be the
    # relevant price we want to display, but that's not handled for now - if there's no price within the granularity
    # period, it'll be rendered as a *missing* value.
    date_point_start = one_day_ago - timedelta(minutes=settings.CHART_GRANULARITY)

    prices = Price.objects.filter(datetime__gte=date_point_start).order_by('datetime')

    price_history = [
        ['Tid', 'Kjøp', 'Salg'],
    ]

    date_point = one_day_ago
    price_index = 0
    price_count = len(prices)
    previous_date_point = date_point - timedelta(minutes=settings.CHART_GRANULARITY)
    relevant_price = None
    while date_point <= now:
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
                relevant_price = price

                # Iterate to see if next price might be relevant too
                price_index += 1
                continue
            elif price.datetime > date_point:
                # Nope, this price is actually after the current date point; stop iterating, we'll check it again next
                # date point
                break
            else:
                raise Exception("This should never *ever* happen")

        if relevant_price is None:
            # This might be the case if it's an early range and there hasn't been any price recorded yet
            buy_price = None
            sell_price = None
        else:
            # The relevant price will now either be leftover from a previous range or a new relevant one
            buy_price = float(round(relevant_price.buy_price, 2))
            sell_price = float(round(relevant_price.sell_price, 2))

        price_history.append([
            date_point.strftime("%H:%M"),
            buy_price,
            sell_price,
        ])

        previous_date_point = date_point
        date_point += timedelta(minutes=settings.CHART_GRANULARITY)

    return price_history
