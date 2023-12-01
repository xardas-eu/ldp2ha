from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.typing import DiscoveryInfoType
from .const import DOMAIN
from typing import Any
from .ldp import LedDimmerPro, client
from .ldp.channel import LDPChannel
import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.const import CONF_IP_ADDRESS
from .const import DOMAIN

async def async_setup(hass: core.HomeAssistant, config: dict):
    """Set up the LDP component."""
    hass.data[DOMAIN] = {}
    return True


class LDPFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle LDP flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate the IP
            ldp_client = LedDimmerPro(user_input[CONF_IP_ADDRESS])
            is_valid = await ldp_client.is_ldp()
            if is_valid:
                return self.async_create_entry(
                    title="LDP",
                    data={
                        CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS],
                    },
                )
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_IP_ADDRESS): str,
                }
            ),
            errors=errors,
        )