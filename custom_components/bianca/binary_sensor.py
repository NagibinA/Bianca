"""Binary sensor for Bianca device availability."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import BiancaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca binary sensor."""
    coordinator: BiancaDataUpdateCoordinator = entry.runtime_data
    ip_address = entry.data[CONF_IP_ADDRESS]
    async_add_entities([BiancaPingBinarySensor(coordinator, entry, ip_address)], True)


class BiancaPingBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for device availability."""

    def __init__(
        self, 
        coordinator: BiancaDataUpdateCoordinator,
        entry: ConfigEntry, 
        ip_address: str
    ) -> None:
        """Initialize the ping sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._ip_address = ip_address
        self._attr_name = f"{entry.title} Доступность"
        self._attr_unique_id = f"{entry.entry_id}_ping"
        self._attr_icon = "mdi:network"
        self._attr_device_class = "connectivity"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._ip_address)},
        }

    @property
    def is_on(self) -> bool:
        """Return true if device is online."""
        if self.coordinator.data is None:
            return False
        # Если есть данные от координатора — устройство доступно
        return True
