import logging
from typing import Any, Callable, List, Optional
from homeassistant.components.select import SelectEntity
from .const import DOMAIN
from .ldp import LedDimmerPro
from .ldp.channel import LDPChannel

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up LDP select entities from a config entry."""
    ldp_client = hass.data[DOMAIN][config_entry.entry_id]["client"]
    channels = await ldp_client.get_channels()


    entities = []
    for channel in channels:
        entity = ChannelSelect(ldp_client, channel, config_entry.entry_id)
        await entity.async_init()
        entities.append(entity)

    # entities = [ChannelSelect(ldp_client, channel, config_entry.entry_id) for channel in channels]
    hass.data[DOMAIN][config_entry.entry_id]["entities"].extend(entities)

    async_add_entities(entities, True)


class ChannelSelect(SelectEntity):
    """Representation of a LedDimmerPro Channel Select entity"""

    _option_to_state = {"AUTO": 0, "ON": 1, "OFF": 2}
    _state_to_option = {0: "AUTO", 1: "ON", 2: "OFF"}
    channel: LDPChannel

    def __init__(self, client: LedDimmerPro, channel: LDPChannel, entry_id: str):
        self._client = client
        self.channel = channel
        self._entry_id = entry_id
        self._device_info = None

    @property
    def device_info(self):
        _LOGGER.info('HEHE devicew info called: {}'.format(self._device_info))
        """Return information about the device."""
        return self._device_info

    async def async_init(self):
        sw_version = await self._client.ldp_version()
        serial_number = await self._client.serial_number()
        self._device_info = {
            "identifiers": {(DOMAIN, serial_number)},
            "name": "LDP",
            "manufacturer": "Roman Linde",
            "model": "LedDimmerProV6",
            "sw_version": sw_version,
        }

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"select.ldp_{self._entry_id}_channel_{self.channel.id}"

    @property
    def name(self):
        """Return the name of the select."""
        return f"LDP {self.channel.name}"

    @property
    def options(self) -> list:
        """Return a list of selectable options."""
        return list(self._option_to_state.keys())

    @property
    def current_option(self):
        """Return the current selected channel state."""
        return self._state_to_option[self.channel.state]

    async def async_select_option(self, option: str) -> None:
        """Action to be performed when an option is selected."""
        await self.channel.set_state(self._option_to_state[option])
