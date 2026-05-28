"""Binary sensor platform for Bianca integration."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    OPTION_NAMES,
    KEY_STEAM,
    OPT_KEYS,
)
from .coordinator import BiancaDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca binary sensors based on a config entry."""
    coordinator = entry.runtime_data.coordinator
    
    entities = []
    
    # Steam binary sensor
    entities.append(BiancaSteamBinarySensor(coordinator, entry))
    
    # Opt1 - Opt9 binary sensors
    for opt_key in OPT_KEYS:
        entities.append(BiancaOptionBinarySensor(coordinator, entry, opt_key))
    
    async_add_entities(entities, True)


class BiancaSteamBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Steam binary sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry) -> None:
        """Initialize the steam sensor."""
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} Пар"
        self._attr_unique_id = f"{entry.entry_id}_steam"
        self._attr_icon = "mdi:water-vapor"
        self._attr_should_poll = False

    @property
    def is_on(self) -> bool | None:
        """Return true if steam is on."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(KEY_STEAM)
        return value == "1"


class BiancaOptionBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for Opt1-Opt9 options."""

    def __init__(
        self,
        coordinator: BiancaDataUpdateCoordinator,
        entry,
        opt_key: str,
    ) -> None:
        """Initialize the option sensor."""
        super().__init__(coordinator)
        self._opt_key = opt_key
        option_name = OPTION_NAMES.get(opt_key, opt_key)
        self._attr_name = f"{entry.title} {option_name}"
        self._attr_unique_id = f"{entry.entry_id}_{opt_key}"
        self._attr_icon = "mdi:toggle-switch"
        self._attr_should_poll = False

    @property
    def is_on(self) -> bool | None:
        """Return true if option is on."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self._opt_key)
        return value == "1"
