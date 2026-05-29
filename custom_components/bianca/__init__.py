"""The Bianca integration."""
from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import timedelta

import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.components.frontend import add_extra_js_url

from .const import DOMAIN, API_ENDPOINT, DEFAULT_SCAN_INTERVAL, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bianca from a config entry."""
    ip_address = entry.data[CONF_IP_ADDRESS]
    device_name = entry.data.get("device_name", "Bianca")
    
    await async_register_custom_icons(hass)
    
    coordinator = BiancaDataUpdateCoordinator(hass, ip_address)
    await coordinator.async_config_entry_first_refresh()
    
    device_registry = async_get_device_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, ip_address)},
        name=device_name,
        manufacturer="Candy",
        model="Bianca",
        configuration_url=f"http://{ip_address}/http-read.json?encrypted=0",
    )
    
    entry.runtime_data = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_register_custom_icons(hass: HomeAssistant) -> None:
    """Register custom icons from integration folder."""
    if hasattr(hass.data, "bianca_icons_registered"):
        return
    
    icons_path = hass.config.path("custom_components/bianca/bianca-icons.js")
    
    if not os.path.exists(icons_path):
        _LOGGER.warning("Icon file not found: %s", icons_path)
        return
    
    www_dir = hass.config.path("www/community/bianca")
    www_icons_path = hass.config.path("www/community/bianca/bianca-icons.js")
    
    if not os.path.exists(www_icons_path):
        try:
            os.makedirs(www_dir, exist_ok=True)
            shutil.copy2(icons_path, www_icons_path)
            _LOGGER.info("Copied icons to %s", www_icons_path)
        except Exception as e:
            _LOGGER.error("Failed to copy icons: %s", e)
            return
    
    add_extra_js_url(hass, "/local/community/bianca/bianca-icons.js")
    
    hass.data["bianca_icons_registered"] = True
    _LOGGER.info("Registered custom icons for Bianca")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class BiancaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the device."""

    def __init__(self, hass: HomeAssistant, ip_address: str) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.ip_address = ip_address
        self._url = API_ENDPOINT.format(ip_address)

    async def _async_update_data(self) -> dict:
        """Fetch data from device."""
        session = async_get_clientsession(self.hass)
        
        try:
            async with async_timeout.timeout(10):
                async with session.get(self._url) as response:
                    if response.status == 200:
                        text = await response.text()
                        try:
                            data = json.loads(text)
                            return data.get("statusLavatrice", {})
                        except json.JSONDecodeError as e:
                            _LOGGER.error("JSON decode error: %s", e)
                            raise UpdateFailed(f"JSON decode error: {e}")
                    else:
                        raise UpdateFailed(f"HTTP error {response.status}")
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}")
