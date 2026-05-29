"""Binary sensor for Bianca device availability."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca binary sensor."""
    ip_address = entry.data[CONF_IP_ADDRESS]
    sensor = BiancaPingBinarySensor(entry, ip_address)
    async_add_entities([sensor], True)
    
    # Запускаем периодическую проверку ping
    async def async_update_ping(now=None):
        await sensor.async_update()
    
    # Обновляем каждые 30 секунд
    async_track_time_interval(hass, async_update_ping, timedelta(seconds=30))


class BiancaPingBinarySensor(BinarySensorEntity):
    """Binary sensor for device availability via ping."""

    def __init__(self, entry: ConfigEntry, ip_address: str) -> None:
        """Initialize the ping sensor."""
        self._entry = entry
        self._ip_address = ip_address
        self._attr_name = f"{entry.title} Доступность"
        self._attr_unique_id = f"{entry.entry_id}_ping"
        self._attr_icon = "mdi:network"
        self._attr_device_class = "connectivity"
        self._available = False

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._ip_address)},
        }

    @property
    def is_on(self) -> bool:
        """Return true if device is online."""
        return self._available

    async def async_update(self) -> None:
        """Ping the device."""
        try:
            # Асинхронный ping через subprocess
            process = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "2", self._ip_address,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()
            self._available = process.returncode == 0
        except Exception as e:
            _LOGGER.error("Ping failed for %s: %s", self._ip_address, e)
            self._available = False
