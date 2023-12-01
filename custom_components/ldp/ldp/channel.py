from .client import LDPAPIClient, STATE_ON, STATE_OFF, STATE_AUTO


class LDPChannel(object):
    client: LDPAPIClient = None
    id = 0
    name = ''
    is_inverted: bool = False
    is_relay: bool = False
    is_temperature_controlled: bool = False
    temp_min: int = 0
    temp_max: int = 0
    wattage: int = 0
    state: int = 0
    color: str = ''

    def __init__(self, client: LDPAPIClient, body: list):
        (
            default,
            channel_id,
            name,
            is_inverted,
            is_relay,
            is_temperature_controlled,
            temp_min,
            temp_max,
            wattage,
            state,
            color
        ) = body

        self.client = client
        self.id = int(channel_id)
        self.name = name
        self.is_inverted = bool(is_inverted)
        self.is_relay = bool(is_relay)
        self.is_temperature_controlled = bool(is_temperature_controlled)
        self.temp_min = int(temp_min)
        self.temp_max = int(temp_max)
        self.wattage = int(wattage)
        self.state = int(state)
        self.color = color

    async def auto(self):
        await self.set_state(STATE_AUTO)

    async def turn_on(self):
        await self.set_state(STATE_ON)

    async def turn_off(self):
        await self.set_state(STATE_OFF)

    async def toggle(self):
        if self.state == STATE_AUTO:
            raise RuntimeError("Cannot toggle channel #{}: is in automatic mode.".format(self.id))

        await self.set_state(STATE_OFF if self.is_on() else STATE_ON)

    def is_on(self) -> bool:
        return self.state == STATE_ON

    def is_auto(self) -> bool:
        return self.state == STATE_AUTO

    async def test(self, value: int) -> None:
        await self.client.test(self.id-1, value)

    async def set_state(self, state: int):
        await self.client.set_state(self.id, state)
        self.state = state
