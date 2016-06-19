import base64
import os

from .base import * # noqa

DEBUG = False
SECRET_KEY = base64.b64decode(os.environ['SECRET_KEY'])
DB_URL = "postgresql://postgres:@postgis/priceticker"
