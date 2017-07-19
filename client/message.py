from message_type import MessageType
import datetime
class Message:
    #change this
    def __init__(self, type, payload, timestamp, alias = None):
        self._type = type
        self._payload = payload
        self._alias = alias
        self._time = timestamp

    def get_time(self):
        return self._time
    def get_alias(self):
        return self._alias
    def set_alias(self, alias):
        self._alias = alias
    def get_payload(self):
        return self._payload
    def get_type(self):
        return self._type