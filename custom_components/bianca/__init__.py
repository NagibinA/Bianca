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
    
    _LOGGER.info("Found icons file at: %s", icons_path)
    
    # Путь в www/community/bianca/
    www_dir = hass.config.path("www/community/bianca")
    www_icons_path = hass.config.path("www/community/bianca/bianca-icons.js")
    version_file_path = hass.config.path("www/community/bianca/version.txt")
    
    # Текущая версия интеграции из manifest.json
    manifest_path = hass.config.path("custom_components/bianca/manifest.json")
    current_version = "1.0.16"
    try:
        def read_manifest():
            with open(manifest_path, "r") as f:
                return json.load(f)
        manifest = await asyncio.to_thread(read_manifest)
        current_version = manifest.get("version", "1.0.17")
    except Exception as e:
        _LOGGER.warning("Failed to read manifest: %s", e)
    
    # Проверяем, нужно ли обновлять файлы
    need_copy = False
    if not os.path.exists(www_icons_path):
        need_copy = True
        _LOGGER.debug("Icon file doesn't exist, will copy")
    elif os.path.exists(version_file_path):
        try:
            def read_version():
                with open(version_file_path, "r") as f:
                    return f.read().strip()
            saved_version = await asyncio.to_thread(read_version)
            if saved_version != current_version:
                need_copy = True
                _LOGGER.debug("Version mismatch: %s vs %s, will update", saved_version, current_version)
            else:
                _LOGGER.debug("Version match: %s, no update needed", current_version)
        except Exception as e:
            _LOGGER.warning("Failed to read version file: %s", e)
            need_copy = True
    else:
        need_copy = True
        _LOGGER.debug("Version file doesn't exist, will copy")
    
    # Копируем иконки если нужно
    if need_copy:
        try:
            os.makedirs(www_dir, exist_ok=True)
            _LOGGER.debug("Created directory: %s", www_dir)
            
            # Выполняем копирование в потоке
            await asyncio.to_thread(shutil.copy2, icons_path, www_icons_path)
            _LOGGER.info("Copied icons to %s", www_icons_path)
            
            # Сохраняем версию в потоке
            def write_version():
                with open(version_file_path, "w") as f:
                    f.write(current_version)
            await asyncio.to_thread(write_version)
            _LOGGER.debug("Saved version: %s", current_version)
        except Exception as e:
            _LOGGER.error("Failed to copy icons: %s", e)
            return
    else:
        _LOGGER.debug("Icons are up to date, skipping copy")
    
    # Копируем изображение стиральной машины
    machine_image_src = hass.config.path("custom_components/bianca/brand/original.png")
    machine_image_dest = hass.config.path("www/community/bianca/original.png")
    
    if os.path.exists(machine_image_src):
        try:
            if need_copy or not os.path.exists(machine_image_dest):
                await asyncio.to_thread(shutil.copy2, machine_image_src, machine_image_dest)
                _LOGGER.info("Copied machine image to %s", machine_image_dest)
        except Exception as e:
            _LOGGER.error("Failed to copy machine image: %s", e)
    
    # Копируем JS файл дашборда
    dashboard_js_src = hass.config.path("custom_components/bianca/dashboard/bianca-dashboard.js")
    dashboard_js_dest = hass.config.path("www/community/bianca/bianca-dashboard.js")
    
    if os.path.exists(dashboard_js_src):
        try:
            if need_copy or not os.path.exists(dashboard_js_dest):
                os.makedirs(www_dir, exist_ok=True)
                await asyncio.to_thread(shutil.copy2, dashboard_js_src, dashboard_js_dest)
                _LOGGER.info("Copied dashboard JS to %s", dashboard_js_dest)
        except Exception as e:
            _LOGGER.error("Failed to copy dashboard JS: %s", e)
    
    # Регистрируем URL иконок и дашборда
    if "bianca_assets_registered" not in hass.data:
        try:
            add_extra_js_url(hass, "/local/community/bianca/bianca-icons.js")
            add_extra_js_url(hass, "/local/community/bianca/bianca-dashboard.js")
            _LOGGER.info("Registered extra JS URLs for Bianca")
        except Exception as e:
            _LOGGER.error("Failed to register extra JS URLs: %s", e)
            return
    
    hass.data["bianca_assets_registered"] = True
    _LOGGER.info("Registered custom assets for Bianca")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Очищаем хранилище статуса доступности
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        del hass.data[DOMAIN][entry.entry_id]
    
    # Удаляем сервисы
    hass.services.async_remove(DOMAIN, "start_washing")
    hass.services.async_remove(DOMAIN, "stop_washing")
    
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class BiancaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the device."""

    def __init__(self, hass: HomeAssistant, ip_address: str, entry_id: str) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.ip_address = ip_address
        self._url = API_ENDPOINT.format(ip_address)
        self._last_valid_data = None
        self._entry_id = entry_id
        self._api_response_status = "NO RESPONSE"

    @property
    def device_available(self) -> bool:
        """Return device availability status from global storage."""
        return self.hass.data.get(DOMAIN, {}).get(self._entry_id, {}).get("available", False)
    
    @property
    def api_response_status(self) -> str:
        """Return the last API response status."""
        return self._api_response_status

    async def _async_update_data(self) -> dict:
        """Fetch data from device."""
        if not self.device_available:
            _LOGGER.debug("Device not available, skipping data update")
            if self._last_valid_data is not None:
                return self._last_valid_data
            return {}
        
        session = async_get_clientsession(self.hass)
        
        try:
            async with async_timeout.timeout(10):
                async with session.get(self._url) as response:
                    if response.status == 200:
                        text = await response.text()
                        try:
                            data = json.loads(text)
                            
                            if "response" in data:
                                self._api_response_status = data["response"]
                                _LOGGER.debug("API response status: %s", self._api_response_status)
                                if self._last_valid_data is not None:
                                    return self._last_valid_data
                                raise UpdateFailed(f"API error: {self._api_response_status}")
                            
                            if "statusLavatrice" in data:
                                self._api_response_status = "OK"
                                self._last_valid_data = data.get("statusLavatrice", {})
                                return self._last_valid_data
                            else:
                                self._api_response_status = "UNKNOWN FORMAT"
                                _LOGGER.debug("Unknown response format: %s", text[:200])
                                if self._last_valid_data is not None:
                                    return self._last_valid_data
                                raise UpdateFailed("Unknown response format from device")
                                
                        except json.JSONDecodeError as e:
                            self._api_response_status = "PARSE ERROR"
                            _LOGGER.error("JSON decode error: %s", e)
                            if self._last_valid_data is not None:
                                return self._last_valid_data
                            raise UpdateFailed(f"JSON decode error: {e}")
                    else:
                        self._api_response_status = f"HTTP {response.status}"
                        _LOGGER.error("HTTP error: %s", response.status)
                        if self._last_valid_data is not None:
                            return self._last_valid_data
                        raise UpdateFailed(f"HTTP error {response.status}")
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            if self._last_valid_data is not None:
                return self._last_valid_data
            raise UpdateFailed(f"Error fetching data: {err}")
