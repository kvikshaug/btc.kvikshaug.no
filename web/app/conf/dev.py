import os

from .base import * # noqa

DEBUG = True
SECRET_KEY = os.urandom(24)
