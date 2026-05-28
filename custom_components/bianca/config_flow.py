"""Config flow for Bianca integration."""

import logging
from typing import Any

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, API_ENDPOINT

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): str,
    }
)


async def validate_ip_address(hass: HomeAssistant, ip_address: str) -> bool:
    """Validate the IP address by making a request to the device."""
    url = API_ENDPOINT.format(ip_address)
    
    try:
        async with async_timeout.timeout(10):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if expected data structure exists
                        if "statusLavatrice" in data:
                            return True
                    return False
    except Exception as e:
        _LOGGER.error("Error connecting to Bianca device at %s: %s", ip_address, e)
        return False


class BiancaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bianca."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            ip_address = user_input[CONF_IP_ADDRESS]
            
            # Check if already configured
            await self.async_set_unique_id(ip_address)
            self._abort_if_unique_id_configured()
            
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
            description_placeholders={
                "example": "192.168.1.31",
            },
        )
