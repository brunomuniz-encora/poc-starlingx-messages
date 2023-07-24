class CircularQueue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.tail = -1
        self.head = 0
        self.size = 0

    def enqueue(self, item):
        if self.size == self.capacity:
            self.dequeue()

        self.tail = (self.tail + 1) % self.capacity
        self.queue[self.tail] = item
        self.size = self.size + 1

    def dequeue(self):
        if self.size == 0:
            return

        item = self.queue[self.head]
        self.head = (self.head + 1) % self.capacity
        self.size = self.size - 1
        return item

    def get_items(self):
        if self.size == 0:
            return []

        if self.head < self.tail:
            return self.queue[self.head:self.tail + 1]
        return self.queue[self.head:] + self.queue[:self.tail + 1]
