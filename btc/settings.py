# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_configuration = os.environ.get('DJANGO_CONFIGURATION', 'dev').lower()

from btc.conf.prod import *
from btc.conf.private.prod import *

from btc.conf.dev import *
from btc.conf.private.dev import *
