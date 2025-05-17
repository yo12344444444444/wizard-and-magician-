import threading

class BotCache:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()

    def get_bot(self, bot_id):
        with self._lock:
            return self._cache.get(bot_id)

    def set_bot(self, bot_id, bot_data):
        with self._lock:
            self._cache[bot_id] = bot_data

    def update_bot(self, bot_id, updates: dict):
        with self._lock:
            if bot_id in self._cache:
                self._cache[bot_id].update(updates)

    def get_all_bots(self):
        with self._lock:
            return dict(self._cache)  # shallow copy

    def remove_bot(self, bot_id):
        with self._lock:
            self._cache.pop(bot_id, None)
