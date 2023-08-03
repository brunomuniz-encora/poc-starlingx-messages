from collections import defaultdict


class CircularTimeseriesDict:
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = defaultdict(int)
        self.oldest = None
        self.size = 0

    def enqueue(self, key, value):
        # This is not thread safe so adjusting shamelessly with >= instead of =
        if self.size >= self.capacity \
                and key not in self.queue\
                and key != self.oldest:
            self.dequeue()

        if self.oldest is None or key < self.oldest:
            self.oldest = key
        self.queue[key] += value
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            return

        del self.queue[self.oldest]
        self.size -= 1
        self.oldest = None
        for key in self.queue:
            if self.oldest is None or key < self.oldest:
                self.oldest = key

    def items(self):
        return self.queue.items()
