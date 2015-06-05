# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_configuration = os.environ.get('DJANGO_CONFIGURATION', 'dev').lower()

from btc.conf.prod import *
from btc.conf.private.prod import *

if _configuration == 'dev':
    from btc.conf.dev import *
    from btc.conf.private.dev import *

try:
    from btc.conf.local import *
except ImportError:
    pass

logger = logging.getLogger('btc')
logger.info("Loaded settings from %s configuration..." % _configuration)
