from datetime import datetime, timedelta
import locale
import logging
import os
import json

from flask import Flask, render_template, jsonify, abort

from chart import get_price_history
from conf import settings
from database import db_session
import filters
from models import Price

locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.config.update(settings)
app.register_blueprint(filters.blueprint)

@app.route('/')
def home():
    now = settings['TIMEZONE'].fromutc(datetime.utcnow())
    last_price = Price.last()
    if last_price is not None:
        current_price = {
            'buy': last_price.btcnok(rate=settings['BUY_RATE']),
            'sell': last_price.btcnok(rate=settings['SELL_RATE']),
        }
    else:
        current_price = None

    context = {
        'current_price': current_price,
        'price_history': json.dumps(get_price_history(app)),
        'now': now,
    }
    return render_template('home.html', **context)

@app.route('/ticker')
def ticker():
    last_price = Price.last()
    if last_price is not None:
        return jsonify(btcnok={
            'buy': str(round(last_price.btcnok(rate=settings['BUY_RATE']), 2)),
            'sell': str(round(last_price.btcnok(rate=settings['SELL_RATE']), 2)),
        })
    else:
        abort(503)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
