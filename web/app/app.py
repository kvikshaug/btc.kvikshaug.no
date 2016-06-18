from datetime import datetime, timedelta
import locale
import logging
import os
import json

from flask import Flask, render_template

from chart import get_price_history
from database import db_session
import filters
from models import Price

locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.config.from_object('conf.%s' % os.environ['CONFIGURATION'])
app.register_blueprint(filters.blueprint)

@app.route('/')
def home():
    last_price = db_session.query(Price).order_by(Price.datetime.desc())[0]

    # Check the age of the last price. If it's too old, there might not have been any trades for a while, or more
    # likely; the priceticker has stopped.
    acceptable_age = timedelta(minutes=15)
    now = app.config['TIMEZONE'].fromutc(datetime.utcnow())
    if app.config['TIMEZONE'].fromutc(last_price.datetime) + acceptable_age < now:
        logger.warning(
            "Last trade price is too old",
            extra={'last_price': last_price, 'now': now},
        )

    context = {
        'current_price': {
            'buy': last_price.btcnok(rate=app.config['BUY_RATE']),
            'sell': last_price.btcnok(rate=app.config['SELL_RATE']),
        },
        'price_history': json.dumps(get_price_history(app)),
        'now': now,
    }
    return render_template('home.html', **context)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
