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
    
    # Инициализируем хранилище
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if entry.entry_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN][entry.entry_id]["available"] = False
    
    # Регистрируем кастомные иконки и дашборд
    await async_register_assets(hass)
    
    coordinator = BiancaDataUpdateCoordinator(hass, ip_address, entry.entry_id)
    
    # Сохраняем ссылку на координатор
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator
    hass.data[DOMAIN][entry.entry_id]["ip_address"] = ip_address
    
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
    
    # Регистрация сервисов
    async def handle_start_washing(call):
        """Handle start washing service."""
        ip_address = entry.data[CONF_IP_ADDRESS]
        
        # Получаем значения из всех select
        program_select = hass.states.get("select.bianca_program")
        temperature_select = hass.states.get("select.bianca_temperature")
        spin_select = hass.states.get("select.bianca_spin")
        delay_select = hass.states.get("select.bianca_delay_start")
        soil_select = hass.states.get("select.bianca_soil")
        steam_select = hass.states.get("select.bianca_steam")
        prewash_select = hass.states.get("select.bianca_pre_wash")
        hygiene_select = hass.states.get("select.bianca_hygiene")
        anticrease_select = hass.states.get("select.bianca_anti_crease")
        nightspin_select = hass.states.get("select.bianca_night_spin")
        extrarinse_select = hass.states.get("select.bianca_extra_rinse")
        aquaplus_select = hass.states.get("select.bianca_aqua_plus")
        zoom_select = hass.states.get("select.bianca_zoom")
        
        # StSt (Start Status)
        StSt = 1
        
        # DelVl (Delay Value)
        delay_str = delay_select.state if delay_select else "Нет"
        DelVl = {
            "Нет": 0, "30 мин": 1, "1 час": 2, "1 час 30 мин": 3, "2 часа": 4, "2 часа 30 мин": 5,
            "3 часа": 6, "3 часа 30 мин": 7, "4 часа": 8, "4 час 30 мин": 9, "5 часов": 10,
            "5 часов 30 мин": 11, "6 часов": 12, "6 часов 30 мин": 13, "7 часов": 14,
            "7 часов 30 мин": 15, "8 часов": 16, "8 часов 30 мин": 17, "9 часов": 18,
            "9 часов 30 мин": 19, "10 часов": 20, "10 часов 30 мин": 21, "11 часов": 22,
            "11 часов 30 мин": 23, "12 часов": 24, "12 часов 30 мин": 25, "13 часов": 26,
            "13 часов 30 мин": 27, "14 часов": 28, "14 часов 30 мин": 29, "15 часов": 30,
            "15 часов 30 мин": 31, "16 часов": 32, "16 часов 30 мин": 33, "17 часов": 34,
            "17 часов 30 мин": 35, "18 часов": 36, "18 часов 30 мин": 37, "19 часов": 38,
            "19 часов 30 мин": 39, "20 часов": 40, "20 часов 30 мин": 41, "21 час": 42,
            "21 час 30 мин": 43, "22 часа": 44, "22 часа 30 мин": 45, "23 часа": 46,
            "23 часа 30 мин": 47, "24 часа": 48
        }.get(delay_str, 0)
        
        # PrNm (Program Number)
        program_str = program_select.state if program_select else "Хлопок: Интенсивная стирка"
        PrNm = {
            "Хлопок: Интенсивная стирка": 1, "Хлопок": 2, "Синтетика и цветные ткани": 3,
            "Шерсть": 4, "Деликатная": 5, "Perfect 20°C": 6, "Полоскание": 7,
            "Слив + Отжим": 8, "Сохранить свежесть": 13, "Perfect rapid 59 минут": 15,
            "Быстрая": 16
        }.get(program_str, 0)
        
        # PrCode (Program Code)
        PrCode = {
            "Хлопок: Интенсивная стирка": 65, "Хлопок": 2, "Синтетика и цветные ткани": 3,
            "Шерсть": 5, "Деликатная": 4, "Perfect 20°C": 11, "Полоскание": 35,
            "Слив + Отжим": 129, "Сохранить свежесть": 41, "Perfect rapid 59 минут": 8,
            "Быстрая": 7
        }.get(program_str, 0)
        
        # PrStr (Program String)
        PrStr = "test"
        
        # TmpTgt (Temperature Target)
        temp_str = temperature_select.state if temperature_select else "60°C"
        TmpTgt = temp_str.replace("°C", "")
        
        # SLevTgt (Soil Level Target)
        soil_str = soil_select.state if soil_select else "Нет"
        SLevTgt = {"Нет": 0, "Мало": 1, "Нормально": 2, "Очень": 3}.get(soil_str, 0)
        
        # SpdTgt (Speed Target)
        spin_str = spin_select.state if spin_select else "1000 об/мин"
        SpdTgt = {
            "0 об/мин": 0, "400 об/мин": 4, "500 об/мин": 5, "600 об/мин": 6,
            "700 об/мин": 7, "800 об/мин": 8, "900 об/мин": 9, "1000 об/мин": 10,
            "1100 об/мин": 11, "1200 об/мин": 12, "1300 об/мин": 13, "1400 об/мин": 14
        }.get(spin_str, 10)
        
        # Stm (Steam)
        steam_str = steam_select.state if steam_select else "Без пара"
        Stm = 5 if steam_str == "С паром" else 0
        
        # OptMsk1 (Options Mask 1)
        OptMsk1 = 0
        if prewash_select and prewash_select.state == "Есть":
            OptMsk1 += 1
        if hygiene_select and hygiene_select.state == "Есть":
            OptMsk1 += 2
        if anticrease_select and anticrease_select.state == "Есть":
            OptMsk1 += 4
        if nightspin_select and nightspin_select.state == "Есть":
            OptMsk1 += 8
        if extrarinse_select:
            rinse_val = extrarinse_select.state
            if rinse_val == "1 полоскание":
                OptMsk1 += 16
            elif rinse_val == "2 полоскания":
                OptMsk1 += 32
            elif rinse_val == "3 полоскания":
                OptMsk1 += 64
        if aquaplus_select and aquaplus_select.state == "Есть":
            OptMsk1 += 128
        
        # OptMsk2 (Options Mask 2)
        OptMsk2 = 1 if (zoom_select and zoom_select.state == "Есть") else 0
        
        # Формируем URL
        url = (
            f"http://{ip_address}/http-write.json?encrypted=0&Write=1"
            f"&StSt={StSt}&DelVl={DelVl}&PrNm={PrNm}&PrCode={PrCode}&PrStr={PrStr}"
            f"&TmpTgt={TmpTgt}&SLevTgt={SLevTgt}&SpdTgt={SpdTgt}"
            f"&OptMsk1={OptMsk1}&OptMsk2={OptMsk2}&Lang=7&Stm={Stm}"
            f"&Dry=0&RecipeId=0&StartCheckUp=0&DispTestOn=0"
        )
        
        # Отправляем запрос
        session = async_get_clientsession(hass)
        try:
            async with async_timeout.timeout(10):
                await session.get(url)
        except Exception:
            pass
        
        # Сбрасываем селект отложенного старта на "Нет"
        delay_select_entity = "select.bianca_delay_start"
        delay_select_state = hass.states.get(delay_select_entity)
        if delay_select_state and delay_select_state.state != "Нет":
            await hass.services.async_call(
                "select", "select_option",
                {"entity_id": delay_select_entity, "option": "Нет"}
            )
    
    async def handle_stop_washing(call):
        """Handle stop washing service."""
        ip_address = entry.data[CONF_IP_ADDRESS]
        url = f"http://{ip_address}/http-write.json?encrypted=0&Write=1&StSt=0"
        session = async_get_clientsession(hass)
        try:
            async with async_timeout.timeout(10):
                await session.get(url)
        except Exception:
            pass
    
    hass.services.async_register(DOMAIN, "start_washing", handle_start_washing)
    hass.services.async_register(DOMAIN, "stop_washing", handle_stop_washing)
    
    return True


async def async_register_assets(hass: HomeAssistant) -> None:
    """Register custom icons and dashboard strategy."""
    if hasattr(hass.data, "bianca_assets_registered"):
        return
    
    icons_path = hass.config.path("custom_components/bianca/bianca-icons.js")
    if not os.path.exists(icons_path):
        return
    
    www_dir = hass.config.path("www/community/bianca")
    www_icons_path = hass.config.path("www/community/bianca/bianca-icons.js")
    version_file_path = hass.config.path("www/community/bianca/version.txt")
    
    manifest_path = hass.config.path("custom_components/bianca/manifest.json")
    current_version = "1.0.27"
    try:
        def read_manifest():
            with open(manifest_path, "r") as f:
                return json.load(f)
        manifest = await asyncio.to_thread(read_manifest)
        current_version = manifest.get("version", "1.0.27")
    except Exception:
        pass
    
    need_copy = False
    if not os.path.exists(www_icons_path):
        need_copy = True
    elif os.path.exists(version_file_path):
        try:
            def read_version():
                with open(version_file_path, "r") as f:
                    return f.read().strip()
            saved_version = await asyncio.to_thread(read_version)
            if saved_version != current_version:
                need_copy = True
        except Exception:
            need_copy = True
    else:
        need_copy = True
    
    if need_copy:
        try:
            os.makedirs(www_dir, exist_ok=True)
            await asyncio.to_thread(shutil.copy2, icons_path, www_icons_path)
            
            def write_version():
                with open(version_file_path, "w") as f:
                    f.write(current_version)
            await asyncio.to_thread(write_version)
        except Exception:
            return
    
    machine_image_src = hass.config.path("custom_components/bianca/brand/original.png")
    machine_image_dest = hass.config.path("www/community/bianca/original.png")
    if os.path.exists(machine_image_src):
        try:
            if need_copy or not os.path.exists(machine_image_dest):
                await asyncio.to_thread(shutil.copy2, machine_image_src, machine_image_dest)
        except Exception:
            pass
    
    dashboard_js_src = hass.config.path("custom_components/bianca/dashboard/bianca-dashboard.js")
    dashboard_js_dest = hass.config.path("www/community/bianca/bianca-dashboard.js")
    if os.path.exists(dashboard_js_src):
        try:
            if need_copy or not os.path.exists(dashboard_js_dest):
                os.makedirs(www_dir, exist_ok=True)
                await asyncio.to_thread(shutil.copy2, dashboard_js_src, dashboard_js_dest)
        except Exception:
            pass
    
    if "bianca_assets_registered" not in hass.data:
        try:
            add_extra_js_url(hass, "/local/community/bianca/bianca-icons.js")
            add_extra_js_url(hass, "/local/community/bianca/bianca-dashboard.js")
        except Exception:
            return
    
    hass.data["bianca_assets_registered"] = True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        del hass.data[DOMAIN][entry.entry_id]
    
    hass.services.async_remove(DOMAIN, "start_washing")
    hass.services.async_remove(DOMAIN, "stop_washing")
    
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class BiancaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the device."""

    def __init__(self, hass: HomeAssistant, ip_address: str, entry_id: str) -> None:
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
        return self.hass.data.get(DOMAIN, {}).get(self._entry_id, {}).get("available", False)
    
    @property
    def api_response_status(self) -> str:
        return self._api_response_status

    async def _async_update_data(self) -> dict:
        """
        Получение данных от устройства.
        
        Если устройство недоступно по пингу - не возвращаем кэш,
        а сразу вызываем исключение UpdateFailed.
        """
        # Если устройство недоступно по пингу - НЕ возвращаем кэш
        if not self.device_available:
            _LOGGER.debug(f"Device {self.ip_address} is offline, raising UpdateFailed")
            raise UpdateFailed("Device is offline")
        
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
                                # API вернул ошибку, но устройство доступно по пингу
                                if self._last_valid_data is not None:
                                    _LOGGER.debug(f"API error but device online, using cached data: {self._api_response_status}")
                                    return self._last_valid_data
                                raise UpdateFailed(f"API error: {self._api_response_status}")
                            
                            if "statusLavatrice" in data:
                                self._api_response_status = "OK"
                                self._last_valid_data = data.get("statusLavatrice", {})
                                return self._last_valid_data
                            else:
                                self._api_response_status = "UNKNOWN FORMAT"
                                if self._last_valid_data is not None:
                                    return self._last_valid_data
                                raise UpdateFailed("Unknown response format from device")
                                
                        except json.JSONDecodeError:
                            self._api_response_status = "PARSE ERROR"
                            if self._last_valid_data is not None:
                                return self._last_valid_data
                            raise UpdateFailed("JSON decode error")
                    else:
                        self._api_response_status = f"HTTP {response.status}"
                        if self._last_valid_data is not None:
                            return self._last_valid_data
                        raise UpdateFailed(f"HTTP error {response.status}")
        except Exception as e:
            # Любая другая ошибка - проверяем доступность устройства
            if self.device_available and self._last_valid_data is not None:
                _LOGGER.debug(f"Device available but error occurred, using cached data: {e}")
                return self._last_valid_data
            _LOGGER.warning(f"Device unavailable or no cache, raising UpdateFailed: {e}")
            raise UpdateFailed(f"Error fetching data: {e}")
