"""Binary sensor for Bianca device availability via ping."""
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
    sensor = BiancaAvailableBinarySensor(hass, entry, ip_address)
    async_add_entities([sensor])


async def async_ping(ip_address: str) -> bool:
    """Check device availability via ping."""
    try:
        process = await asyncio.create_subprocess_exec(
            "ping", "-c", "1", "-W", "2", ip_address,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.wait()
        return process.returncode == 0
    except Exception:
        return False


class BiancaAvailableBinarySensor(BinarySensorEntity):
    """Binary sensor for device availability via ping."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, ip_address: str) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._entry = entry
        self._ip_address = ip_address
        self._attr_unique_id = f"{entry.entry_id}_available"
        self._attr_name = "Bianca Доступность"
        self._attr_icon = "mdi:network"
        self._attr_should_poll = False
        self._state = False
        self._unsub_update = None

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._ip_address)},
        }

    @property
    def is_on(self) -> bool:
        """Return true if device is online."""
        return self._state

    @property
    def icon(self):
        """Return icon based on state."""
        return "mdi:network" if self._state else "mdi:network-off"

    async def async_update_ping(self, now=None) -> None:
        """Update ping state and store in global storage."""
        self._state = await async_ping(self._ip_address)
        
        if DOMAIN in self._hass.data:
            if self._entry.entry_id in self._hass.data[DOMAIN]:
                self._hass.data[DOMAIN][self._entry.entry_id]["available"] = self._state
        
        self.async_write_ha_state()
        
        if self._state and DOMAIN in self._hass.data and self._entry.entry_id in self._hass.data[DOMAIN]:
            coordinator = self._hass.data[DOMAIN].get(self._entry.entry_id, {}).get("coordinator")
            if coordinator:
                await coordinator.async_refresh()

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
            self._unsub_update = None
