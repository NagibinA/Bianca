"""Config flow for Bianca integration."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN, API_ENDPOINT

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): str,
    }
)


async def validate_ip_address(hass, ip_address):
    """Validate the IP address."""
    url = API_ENDPOINT.format(ip_address)
    session = aiohttp_client.async_get_clientsession(hass)
    
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                if "statusLavatrice" in data:
                    return True
            return False
    except Exception as e:
        _LOGGER.error("Validation error: %s", e)
        return False


class BiancaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bianca."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            ip_address = user_input[CONF_IP_ADDRESS]
            
            self._async_abort_entries_match({CONF_IP_ADDRESS: ip_address})
            
            valid = await validate_ip_address(self.hass, ip_address)
            
            if valid:
                return self.async_create_entry(
                    title=f"Bianca ({ip_address})",
                    data=user_input,
                )
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
