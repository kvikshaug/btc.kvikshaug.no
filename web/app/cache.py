from datetime import datetime, timedelta
import threading
import logging

logger = logging.getLogger(__name__)

class MemoryCache(threading.Thread):
    """Simple dict-backed memory cache. Runs a separate thread to clear up expired keys. Note that the thread is
    daemonized and may end abruptly, and therefore should never hold resources that need to be closed."""
    def __init__(self, *args, **kwargs):
        super().__init__(daemon=True, *args, **kwargs)
        self._store = {}
        self._store_lock = threading.Lock()
        self._stop_event = threading.Event()
        self.start()

    def set(self, key, value, retention):
        with self._store_lock:
            self._store[key] = (value, datetime.now() + timedelta(seconds=retention))

    def get(self, key):
        with self._store_lock:
            try:
                value, expiry = self._store[key]
                if expiry <= datetime.now():
                    del self._store[key]
                    return None
                else:
                    return value
            except KeyError:
                return None

    def run(self):
        clear_interval = 60 * 60 # seconds
        while not self._stop_event.is_set():
            with self._store_lock:
                expired_keys = [key for key, (value, expiry) in self._store.items() if expiry <= datetime.now()]
                for key in expired_keys:
                    del self._store[key]
            self._stop_event.wait(clear_interval)

    def stop(self):
        logger.debug("MemoryCache clearer thread stopping")
        self._stop_event.set()

cache = MemoryCache()
