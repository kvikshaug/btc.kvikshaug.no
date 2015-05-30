import json
import socket

from django.conf import settings
from django.core.cache import cache

def get_current():
    price = cache.get('current_price')
    if price is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(settings.PRICE_ADDRESS)

        # The data message will probably never exceed a 4096b buffer, but hey, why take the chance
        chunks = []
        while True:
            chunk = sock.recv(4096)
            if chunk != b'':
                chunks.append(chunk)
            else:
                data = b''.join(chunks).decode('utf-8')
                break

        price = json.loads(data)
        cache.set('current_price', price, 10)

    buy = price * settings.BUY_RATE
    sell = price * settings.SELL_RATE
    return {
        'buy': buy,
        'sell': sell,
    }
