"""The Bianca integration."""

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import BiancaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class RuntimeData:
    """Runtime data for the integration."""
    coordinator: BiancaDataUpdateCoordinator


type BiancaConfigEntry = ConfigEntry[RuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: BiancaConfigEntry) -> bool:
    """Set up Bianca from a config entry."""
    ip_address = entry.data[CONF_IP_ADDRESS]
    
    coordinator = BiancaDataUpdateCoordinator(hass, ip_address)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    entry.runtime_data = RuntimeData(coordinator=coordinator)
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BiancaConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "binary_sensor"]
    )
