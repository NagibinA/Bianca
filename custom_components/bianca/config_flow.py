"""Config flow for Bianca integration."""
from __future__ import annotations

import json
import logging
from typing import Any

import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_INTEGRATION_TITLE, API_ENDPOINT

_LOGGER = logging.getLogger(__name__)

STEP_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): str,
    vol.Optional("device_name", default="Bianca"): str,
})


async def test_connection(hass, ip_address: str) -> bool:
    """Test connection to the device."""
    url = API_ENDPOINT.format(ip_address)
    session = async_get_clientsession(hass)
    
    try:
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    try:
                        data = json.loads(text)
                        return "statusLavatrice" in data
                    except json.JSONDecodeError:
                        _LOGGER.error("Invalid JSON response: %s", text[:200])
                        return False
                return False
    except Exception as e:
        _LOGGER.error("Connection test failed: %s", e)
        return False


class BiancaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bianca."""

    VERSION = 1

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_DATA_SCHEMA)

        errors = {}
        
        # Проверяем соединение, но не блокируем создание интеграции при ошибке
        connected = await test_connection(self.hass, user_input[CONF_IP_ADDRESS])
        
        if not connected:
            _LOGGER.warning(f"Cannot connect to {user_input[CONF_IP_ADDRESS]}, but creating integration anyway")
            # Не показываем ошибку, просто предупреждаем в логе
        
        return self.async_create_entry(
            title=user_input.get("device_name", CONF_INTEGRATION_TITLE),
            data={
                CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS],
                "device_name": user_input.get("device_name", CONF_INTEGRATION_TITLE),
            }
        )
