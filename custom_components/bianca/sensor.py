"""Sensor platform for Bianca integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import BiancaDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca sensors."""
    coordinator: BiancaDataUpdateCoordinator = entry.runtime_data
    
    entities = [
        BiancaWiFiStatusSensor(coordinator, entry),
    ]
    
    async_add_entities(entities)


class BiancaWiFiStatusSensor(CoordinatorEntity, SensorEntity):
    """WiFi status sensor."""

    def __init__(
        self, 
        coordinator: BiancaDataUpdateCoordinator, 
        entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = f"{entry.title} WiFi статус"
        self._attr_unique_id = f"{entry.entry_id}_wifi_status"
        self._attr_icon = "mdi:wifi"

    @property
    def native_value(self) -> str | None:
        """Return the state."""
        if self.coordinator.data is None:
            return None
        
        wifi_status = self.coordinator.data.get("WiFiStatus")
        
        if wifi_status == "1":
            return "Управление разрешено"
        elif wifi_status == "0":
            return "Управление запрещено"
        return wifi_status
