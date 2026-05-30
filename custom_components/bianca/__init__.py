"""The Bianca integration."""
from __future__ import annotations

import json
import logging
import os
import shutil
import asyncio
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
    
    # Инициализируем хранилище статуса доступности
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if entry.entry_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN][entry.entry_id]["available"] = False
    
    # Регистрируем кастомные иконки и дашборд
    await async_register_assets(hass)
    
    coordinator = BiancaDataUpdateCoordinator(hass, ip_address, entry.entry_id)
    
    # Сохраняем ссылку на координатор в глобальном хранилище
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator
    hass.data[DOMAIN][entry.entry_id]["ip_address"] = ip_address
    
    # Пытаемся получить данные, но не блокируем загрузку интеграции при ошибке
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as e:
        _LOGGER.warning(f"Initial connection to {ip_address} failed: {e}. Integration will load anyway.")
    
    # Создаём устройство (всегда, даже если нет связи)
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
    
    # Регистрация сервисов
    async def handle_start_washing(call):
        """Handle start washing service."""
        _LOGGER.info("Start washing called")
        # TODO: Реализовать отправку команды на машину
        url = f"http://{ip_address}/http-write.json?encrypted=0&Write=1&StSt=1"
        session = async_get_clientsession(hass)
        try:
            async with async_timeout.timeout(10):
                async with session.get(url) as response:
                    _LOGGER.info(f"Start washing response: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error starting washing: {e}")
    
    async def handle_stop_washing(call):
        """Handle stop washing service."""
        _LOGGER.info("Stop washing called")
        url = f"http://{ip_address}/http-write.json?encrypted=0&Write=1&StSt=0"
        session = async_get_clientsession(hass)
        try:
            async with async_timeout.timeout(10):
                async with session.get(url) as response:
                    _LOGGER.info(f"Stop washing response: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error stopping washing: {e}")
    
    hass.services.async_register(DOMAIN, "start_washing", handle_start_washing)
    hass.services.async_register(DOMAIN, "stop_washing", handle_stop_washing)
    
    return True


async def async_register_assets(hass: HomeAssistant) -> None:
    """Register custom icons and dashboard strategy."""
    # Проверяем, зарегистрированы ли уже ассеты
    if hasattr(hass.data, "bianca_assets_registered"):
        _LOGGER.debug("Assets already registered")
        return
    
    # Путь к файлу иконок внутри интеграции
    icons_path = hass.config.path("custom_components/bianca/bianca-icons.js")
    _LOGGER.debug("Looking for icons at: %s", icons_path)
    
    if not os.path.exists(icons_path):
        _LOGGER.warning("Icon file not found: %s", icons_path)
        return
