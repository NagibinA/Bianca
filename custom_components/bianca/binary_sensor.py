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


class BiancaPingBinarySensor(BinarySensorEntity):
    """Binary sensor for device availability via ping."""

    def __init__(self, entry: ConfigEntry, ip_address: str) -> None:
        """Initialize the ping sensor."""
        self._entry = entry
        self._ip_address = ip_address
        self._attr_name = f"{entry.title} Доступность"
        self._attr_unique_id = f"{entry.entry_id}_ping"
        self._state = None
        self._unsub_update = None

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._ip_address)},
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if device is online."""
        return self._state

    @property
    def icon(self):
        """Return icon based on state."""
        if self._state is True:
            return "mdi:network"
        return "mdi:network-off"

    async def async_update_ping(self, now=None) -> None:
        """Ping the device."""
        try:
            process = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "2", self._ip_address,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()
            self._state = process.returncode == 0
        except Exception as e:
            _LOGGER.error("Ping failed for %s: %s", self._ip_address, e)
            self._state = False
        
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Start polling when entity is added."""
        await self.async_update_ping()
        self._unsub_update = async_track_time_interval(
            self.hass, self.async_update_ping, timedelta(seconds=30)
        )

    async def async_will_remove_from_hass(self) -> None:
        """Stop polling when entity is removed."""
        if self._unsub_update:
            self._unsub_update()
