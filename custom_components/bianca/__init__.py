"""The Bianca integration - Version 2.5.0."""

from __future__ import annotations

import logging
import os
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN, API_ENDPOINT, DEFAULT_SCAN_INTERVAL, PLATFORMS
from .program_manager import ProgramManager
from .card_mod_installer import ensure_card_mod
from .coordinator import BiancaDataUpdateCoordinator
from .assets import async_register_assets
from .api_views import async_register_views
from .services import async_register_services

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bianca from a config entry."""
    ip_address = entry.data[CONF_IP_ADDRESS]
    device_name = entry.data.get("device_name", "Bianca")
    
    # Установка Card Mod при необходимости
    await ensure_card_mod(hass)
    
    # Инициализируем хранилище
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if entry.entry_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN][entry.entry_id]["available"] = False
    
    # Инициализируем ProgramManager через executor
    def create_program_manager():
        return ProgramManager(hass)
    program_manager = await hass.async_add_executor_job(create_program_manager)
    hass.data[DOMAIN][entry.entry_id]["program_manager"] = program_manager
    
    # Регистрируем кастомные иконки и дашборд
    await async_register_assets(hass)
    
    coordinator = BiancaDataUpdateCoordinator(hass, ip_address, entry.entry_id)
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator
    hass.data[DOMAIN][entry.entry_id]["ip_address"] = ip_address
    hass.data[DOMAIN][entry.entry_id]["started_by_user"] = None
    
    # Пытаемся получить данные
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as e:
        _LOGGER.warning(f"Initial connection to {ip_address} failed: {e}. Integration will load anyway.")
    
    # Создаём устройство
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
    
    # Регистрация API эндпоинтов
    await async_register_views(hass)
    
    # Регистрация сервисов
    await async_register_services(hass, program_manager)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        del hass.data[DOMAIN][entry.entry_id]
    
    hass.services.async_remove(DOMAIN, "start_washing")
    hass.services.async_remove(DOMAIN, "stop_washing")
    
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove Bianca integration - cleanup www files."""
    www_bianca_dir = hass.config.path("www/community/bianca")
    
    def remove_files():
        if os.path.exists(www_bianca_dir):
            files_to_remove = ["version.txt", "bianca-dashboard.js", "bianca-simple.js", "admin.html"]
            for filename in files_to_remove:
                file_path = os.path.join(www_bianca_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    _LOGGER.debug(f"Removed {file_path}")
    
    await hass.async_add_executor_job(remove_files)
    _LOGGER.debug("Bianca files cleaned up, bianca-icons.js preserved")
