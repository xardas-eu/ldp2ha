from .client import LDPAPIClient, NUM_CHANNELS, parse_point_string
from .channel import LDPChannel
from .point import LDPPoint
from time import sleep

"""The LedDimmerPro API client."""


class LedDimmerPro(object):
    channels: dict = {}
    points: dict = {}

    def __init__(self, ip):
        self.client = LDPAPIClient(ip)

    def simulate(self, sim: bool = True):
        self.client.simulate(sim)

    async def is_ldp(self):
        return await self.client.is_ldp()

    async def add_point(self, dimmer_channel: LDPChannel, value: int, time: int = 0, day: int = 0,
                  month: int = 0) -> LDPPoint:
        if not time:
            time = client.get_current_ldp_time()
        point_string = client.get_point_string(dimmer_channel.id, time, value, day, month)
        point_id = await self.client.add_point(point_string)
        return await self.get_point(point_id)

    async def serial_number(self) -> str:
        return await self.client.get_serial_number()

    async def ldp_version(self) -> str:
        return await self.client.get_version()

    async def get_points(self, update: bool = False) -> list[LDPPoint]:
        if not self.points or update:
            for i in range(1, await self.client.get_point_count() + 1):
                try:
                    self.points[i] = self._parse_point(await self.client.get_point(i))
                    sleep(0.05)  # delay a bit
                except ValueError:
                    # "END" received, no more points to read
                    break

        return list(self.points.values())

    async def get_point(self, point_id: int) -> LDPPoint:
        try:
            return self.points[point_id]
        except KeyError:
            # no point, try download
            self.points[point_id] = self._parse_point(await self.client.get_point(point_id))
            return self.points[point_id]

    async def get_channels(self, update: bool = False) -> list[LDPChannel]:
        if not self.channels or update:
            for i in range(1, NUM_CHANNELS + 1):
                self.channels[i] = self._parse_channel(await self.client.get_channel(i))

        return list(self.channels.values())

    async def get_channel_by_index(self, index: str) -> LDPChannel:
        if not self.channels:
            await self.get_channels()

        return self.channels[index]

    async def get_channel_by_name(self, name: str) -> LDPChannel:
        if not self.channels:
            await self.get_channels()

        for dimmer_channel in self.channels.values():
            if dimmer_channel.name == name:
                return dimmer_channel

    async def get_states(self, update: bool = False):
        if update:
            await self.update_states()

        return {dimmer_channel.id: dimmer_channel.state for dimmer_channel in self.channels.values()}

    async def update_states(self):
        if not self.channels:
            await self.get_channels()

        states = await self.client.get_states()
        for channel_id, state in enumerate(states):
            if state.isnumeric():
                self.channels[int(channel_id)].state = int(state)

    def _parse_channel(self, body: list) -> LDPChannel:
        return LDPChannel(self.client, body)

    def _parse_point(self, body: str) -> LDPPoint:
        point = parse_point_string(body)
        return LDPPoint(self.client, self.channels[point['channel_id']], point)
