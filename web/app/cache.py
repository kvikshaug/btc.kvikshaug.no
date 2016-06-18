class DummyCache:
    def set(self, key, value, retention):
        pass

    def get(self, key):
        return None

cache = DummyCache()
