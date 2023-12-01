"""The LDP integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
import logging
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .ldp import LedDimmerPro
from homeassistant.const import CONF_IP_ADDRESS

_LOGGER = logging.getLogger(__name__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SELECT]


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["select"]  # Put here the platforms your integration supports
    )
    if unload_ok:
        client = hass.data[DOMAIN][entry.entry_id]["client"]
        await client.session.close()

        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up LedDimmerPro from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    host = entry.data[CONF_IP_ADDRESS]
    ldp = LedDimmerPro(host)
    hass.data[DOMAIN][entry.entry_id] = {
        "client": ldp,
        "entities": [],
    }

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    async def async_update_data(now):
        """Fetch data from API and update all entities."""
        channel_states = await ldp.get_states(True)
        _LOGGER.debug("Update data retrieved: %s", channel_states)
        for entity in hass.data[DOMAIN][entry.entry_id]["entities"]:
            if entity.channel.id in channel_states:
                entity.channel.state = channel_states[entity.channel.id]
                entity.async_write_ha_state()

    # Run async_update_data method every 60 seconds
    async_track_time_interval(hass, async_update_data, timedelta(seconds=15))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
