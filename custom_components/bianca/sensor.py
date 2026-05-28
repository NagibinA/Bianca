"""Sensor platform for Bianca integration."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BiancaConfigEntry
from .const import KEY_WIFISTATUS
from .coordinator import BiancaDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BiancaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca sensors based on a config entry."""
    coordinator = entry.runtime_data.coordinator
    
    sensors = [
        BiancaWiFiStatusSensor(coordinator, entry),
    ]
    
    async_add_entities(sensors, True)


class BiancaWiFiStatusSensor(CoordinatorEntity, SensorEntity):
    """WiFi status sensor."""

    def __init__(
        self,
        coordinator: BiancaDataUpdateCoordinator,
        entry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} WiFi статус"
        self._attr_unique_id = f"{entry.entry_id}_wifi_status"
        self._attr_icon = "mdi:wifi"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(KEY_WIFISTATUS)
        if value == "1":
            return "Управление разрешено"
        elif value == "0":
            return "Управление запрещено"
        return value
