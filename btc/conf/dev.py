# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from btc.settings import _configuration
from btc.conf.prod import *

if _configuration == 'dev':
    DEBUG = True
