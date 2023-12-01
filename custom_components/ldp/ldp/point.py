from .client import LDPAPIClient
from .channel import LDPChannel
from datetime import datetime, timedelta

MAX_VALUE = 1023


class LDPPoint(object):
    id: int = 0
    client: LDPAPIClient = None
    channel: LDPChannel = None
    month: int = 0
    day: int = 0
    value: int = 0

    def __init__(self, client: LDPAPIClient, channel: LDPChannel, data: dict):
        self.id = data['id']
        self.client = client
        self.channel = channel
        self.value = data['value']
        self.month = data['month']
        self.day = data['day']
        self.time = data['time']

    def datetime(self) -> datetime:
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=self.time)

    def percentage(self, rounding: int = 0) -> float:
        return round((self.value / MAX_VALUE) * 100, rounding)

    def save(self):
        self.client.update_point(self.id, self.as_string())

    def as_string(self) -> str:
        return ":".join(str(v) for v in
            [self.month, self.day, self.channel.id-1, self.time, self.value]
        )

    def delete(self) -> None:
        self.client.delete_point(self.id)
        self.id = 0
