from collections import OrderedDict


class AnswerCache:
    def __init__(self, max_size=100):
        self.max_size = max_size
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None

        # Move recently used entries to the end
        self.cache.move_to_end(key)

        return self.cache[key]

    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)

        self.cache[key] = value

        # Remove the oldest entry if cache is full
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def clear(self):
        self.cache.clear()

    def __len__(self):
        return len(self.cache)