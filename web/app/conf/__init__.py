import importlib
import os

conf_module = importlib.import_module("conf.%s" % os.environ['CONFIGURATION'])

settings = {
    key: getattr(conf_module, key)
    for key in dir(conf_module)
    if key.isupper()
}
