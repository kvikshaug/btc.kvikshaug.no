import logging.config
import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
        'verbose': {
            'format': '%(levelname)s (%(name)s) %(asctime)s\n%(pathname)s:%(lineno)d in %(funcName)s\n%(message)s\n'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': os.environ['SENTRY_DSN'],
        },
        'papertrail': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'simple',
            'address': ('logs2.papertrailapp.com', 58442),
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'sentry'],
    }
}

logging.config.dictConfig(LOGGING)
