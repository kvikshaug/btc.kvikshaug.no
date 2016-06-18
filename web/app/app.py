from datetime import datetime
import locale
import os
import json

from flask import Flask, render_template

import filters

locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

app = Flask(__name__)
app.config.from_object('conf.%s' % os.environ['CONFIGURATION'])
app.register_blueprint(filters.blueprint)

def get_price_history():
    # TODO
    pass

@app.route('/')
def home():
    context = {
        'price': {'buy': None, 'sell': None}, # TODO
        'price_history': json.dumps(get_price_history()),
        'now': datetime.now(),
    }
    return render_template('home.html', **context)
