from shared.concurrent_queue import ConcurrentQueue

class SendMessageHandler:

    def __init__(self, socket):
        self.socket = socket
        self.queue = ConcurrentQueue()