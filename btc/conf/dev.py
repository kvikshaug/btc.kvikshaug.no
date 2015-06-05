# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from btc.settings import _configuration
from btc.conf.prod import *
from btc.conf.private.prod import *

DEBUG = True
INSTALLED_APPS += ('debug_toolbar',)

# Limit btc loggers to console, suppress other loggers
LOGGING['loggers']['btc']['handlers'] = ['console']
LOGGING['loggers']['pusherclient']['handlers'] = []

# Deactivate Sentry
RAVEN_CONFIG['dsn'] = None

# Fallback to local memory in development
CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'btc.kvikshaug.no',
}
