"""The Bianca integration - Version 2.3.2."""

from __future__ import annotations

import json
import logging
import os
import shutil
import asyncio
from datetime import timedelta

import async_timeout
from aiohttp import web
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN, API_ENDPOINT, DEFAULT_SCAN_INTERVAL, PLATFORMS, OPTION_VALUE_TO_CODE, VERSION
from .program_manager import ProgramManager
from .card_mod_installer import ensure_card_mod

_LOGGER = logging.getLogger(__name__)


def get_program_manager(hass) -> ProgramManager:
    """Получает ProgramManager из первой найденной конфигурации Bianca."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return None
    
    entry_id = entries[0].entry_id
    if DOMAIN not in hass.data or entry_id not in hass.data[DOMAIN]:
        return None
    
    return hass.data[DOMAIN][entry_id].get("program_manager")


class BiancaAddProgramFullView(HomeAssistantView):
    """Эндпоинт для добавления программы со всеми опциями и взаимоисключениями."""
    
    url = "/api/bianca/add_program_full"
    name = "api:bianca:add_program_full"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        
        name = data.get("name")
        pr = data.get("Pr")
        pr_code = data.get("PrCode")
        pr_str = data.get("PrStr")
        options = data.get("options", {})
        mutual_exclusion = data.get("mutual_exclusion", [])
        
        if not all([name, pr, pr_code, pr_str]):
            return web.json_response(
                {"success": False, "error": "Не все поля заполнены"},
                status=400
            )
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response(
                {"success": False, "error": "Интеграция Bianca не найдена"},
                status=404
            )
        
        prog_id = program_manager.add_program(name, pr, pr_code, pr_str, options, mutual_exclusion)
        
        return web.json_response({
            "success": True,
            "message": f"Программа '{name}' (ID: {prog_id}) добавлена! Перезапустите Home Assistant.",
            "program_id": prog_id
        })


class BiancaAddMultipleProgramsView(HomeAssistantView):
    """Эндпоинт для массового добавления программ."""
    
    url = "/api/bianca/add_multiple_programs"
    name = "api:bianca:add_multiple_programs"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response(
                {"success": False, "error": "Интеграция Bianca не найдена"},
                status=404
            )
        
        # Извлекаем список программ из разных форматов
        programs_to_add = []
        
        if "programs" in data:
            if isinstance(data["programs"], dict):
                for prog_data in data["programs"].values():
                    programs_to_add.append(prog_data)
            elif isinstance(data["programs"], list):
                programs_to_add = data["programs"]
        else:
            if "name" in data and "Pr" in data:
                programs_to_add = [data]
        
        if not programs_to_add:
            return web.json_response({
                "success": False,
                "error": "Не найден список программ в запросе"
            }, status=400)
        
        added = []
        skipped = []
        errors = []
        
        for prog in programs_to_add:
            name = prog.get("name")
            pr = prog.get("Pr")
            pr_code = prog.get("PrCode", 0)
            pr_str = prog.get("PrStr", "")
            options = prog.get("options", {})
            mutual_exclusion = prog.get("mutual_exclusion", [])
            
            if not name or pr is None:
                errors.append(f"Пропущена программа: нет name или Pr")
                continue
            
            try:
                program_manager.add_program(name, pr, pr_code, pr_str, options, mutual_exclusion)
                added.append(f"{pr} - {name}")
            except Exception as e:
                errors.append(f"{pr} - {name}: {e}")
        
        program_manager._save_config()
        
        return web.json_response({
            "success": True,
            "added": added,
            "skipped": skipped,
            "errors": errors,
            "message": f"Добавлено: {len(added)}, Пропущено: {len(skipped)}, Ошибок: {len(errors)}"
        })


class BiancaGetProgramsView(HomeAssistantView):
    """Эндпоинт для получения списка программ."""
    
    url = "/api/bianca/get_programs"
    name = "api:bianca:get_programs"
    requires_auth = False

    async def get(self, request):
        hass = request.app["hass"]
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response({"success": False, "error": "Интеграция Bianca не найдена"}, status=404)
        
        programs_list = []
        for prog_id, prog in program_manager.programs.items():
            programs_list.append({
                "id": int(prog_id),
                "name": prog.get("name", ""),
                "Pr": prog.get("Pr", 0),
                "PrCode": prog.get("PrCode", 0),
                "PrStr": prog.get("PrStr", "")
            })
        
        return web.json_response({"success": True, "programs": programs_list, "next_id": program_manager.next_id})


class BiancaGetProgramView(HomeAssistantView):
    """Эндпоинт для получения полной информации о программе."""
    
    url = "/api/bianca/get_program/{program_id}"
    name = "api:bianca:get_program"
    requires_auth = False

    async def get(self, request, program_id):
        hass = request.app["hass"]
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response({"success": False, "error": "Интеграция Bianca не найдена"}, status=404)
        
        program = program_manager.get_program(int(program_id))
        if not program:
            return web.json_response({"success": False, "error": f"Program {program_id} not found"}, status=404)
        
        return web.json_response({
            "success": True,
            "program": {
                "id": int(program_id),
                "name": program.get("name", ""),
                "Pr": program.get("Pr", 0),
                "PrCode": program.get("PrCode", 0),
                "PrStr": program.get("PrStr", ""),
                "options": program.get("options", {}),
                "mutual_exclusion": program.get("mutual_exclusion", [])
            }
        })


class BiancaUpdateProgramView(HomeAssistantView):
    """Эндпоинт для обновления программы."""
    
    url = "/api/bianca/update_program"
    name = "api:bianca:update_program"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        
        program_id = data.get("program_id")
        name = data.get("name")
        pr = data.get("Pr")
        pr_code = data.get("PrCode")
        pr_str = data.get("PrStr")
        options = data.get("options", {})
        mutual_exclusion = data.get("mutual_exclusion", [])
        
        if not all([program_id, name, pr, pr_code, pr_str]):
            return web.json_response(
                {"success": False, "error": "Не все поля заполнены"},
                status=400
            )
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response({"success": False, "error": "Интеграция Bianca не найдена"}, status=404)
        
        success = program_manager.update_program(program_id, name, pr, pr_code, pr_str, options, mutual_exclusion)
        
        if not success:
            return web.json_response({"success": False, "error": "Program not found"}, status=404)
        
        return web.json_response({
            "success": True,
            "message": f"Программа '{name}' обновлена! Перезапустите Home Assistant."
        })


class BiancaDeleteProgramView(HomeAssistantView):
    """Эндпоинт для удаления программы."""
    
    url = "/api/bianca/delete_program"
    name = "api:bianca:delete_program"
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        
        program_id = data.get("program_id")
        
        if not program_id:
            return web.json_response(
                {"success": False, "error": "ID программы не указан"},
                status=400
            )
        
        program_manager = get_program_manager(hass)
        if not program_manager:
            return web.json_response({"success": False, "error": "Интеграция Bianca не найдена"}, status=404)
        
        program = program_manager.get_program(program_id)
        if not program:
            return web.json_response({"success": False, "error": f"Программа с ID {program_id} не найдена"}, status=404)
        
        program_name = program.get("name", program_id)
        program_manager.delete_program(program_id)
        
        return web.json_response({
            "success": True,
            "message": f"Программа '{program_name}' удалена! Перезапустите Home Assistant."
        })


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
    
    # Инициализируем ProgramManager
    program_manager = ProgramManager(hass)
    hass.data[DOMAIN][entry.entry_id]["program_manager"] = program_manager
    
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
    
    # Регистрация API эндпоинтов
    hass.http.register_view(BiancaAddProgramFullView)
    hass.http.register_view(BiancaAddMultipleProgramsView)
    hass.http.register_view(BiancaGetProgramsView)
    hass.http.register_view(BiancaGetProgramView)
    hass.http.register_view(BiancaUpdateProgramView)
    hass.http.register_view(BiancaDeleteProgramView)
    
    # Регистрация сервисов
    async def handle_start_washing(call):
        """Handle start washing service."""
        program_select = hass.states.get("select.bianca_program")
        program_name = program_select.state if program_select else None
        
        # Находим программу по имени
        program_id = None
        program = None
        for pid, prog in program_manager.programs.items():
            if prog.get("name") == program_name:
                program_id = int(pid)
                program = prog
                break
        
        if program_id is None:
            _LOGGER.error(f"Unknown program: {program_name}")
            return
        
        values = {}
        for option_key, entity_id in {
            "temperature": "select.bianca_temperature",
            "spin": "select.bianca_spin",
            "soil": "select.bianca_soil",
            "steam": "select.bianca_steam",
            "pre_wash": "select.bianca_pre_wash",
            "hygiene": "select.bianca_hygiene",
            "anti_crease": "select.bianca_anti_crease",
            "night_spin": "select.bianca_night_spin",
            "extra_rinse": "select.bianca_extra_rinse",
            "aqua_plus": "select.bianca_aqua_plus",
            "zoom": "select.bianca_zoom",
        }.items():
            select = hass.states.get(entity_id)
            values[option_key] = select.state if select else "Нет"
        
        delay_select = hass.states.get("select.bianca_delay_start")
        delay_str = delay_select.state if delay_select else "Нет"
        
        StSt = 1
        
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
        
        PrNm = program.get("Pr", 0)
        PrCode = program.get("PrCode", 0)
        PrStr = program.get("PrStr", "test")
        TmpTgt = values["temperature"].replace("°C", "")
        SLevTgt = {"Нет": 0, "Мало": 1, "Нормально": 2, "Очень": 3}.get(values["soil"], 0)
        SpdTgt = {
            "0 об/мин": 0, "400 об/мин": 4, "500 об/мин": 5, "600 об/мин": 6,
            "700 об/мин": 7, "800 об/мин": 8, "900 об/мин": 9, "1000 об/мин": 10,
            "1100 об/мин": 11, "1200 об/мин": 12, "1300 об/мин": 13, "1400 об/мин": 14
        }.get(values["spin"], 10)
        Stm = 5 if values["steam"] == "С паром" else 0
        
        OptMsk1 = 0
        opt_masks = ["pre_wash", "hygiene", "anti_crease", "night_spin", "extra_rinse", "aqua_plus"]
        for opt in opt_masks:
            code_map = OPTION_VALUE_TO_CODE.get(opt, {})
            OptMsk1 += code_map.get(values[opt], 0)
        
        OptMsk2 = 1 if values["zoom"] == "Есть" else 0
        
        url = (
            f"http://{ip_address}/http-write.json?encrypted=0&Write=1"
            f"&StSt={StSt}&DelVl={DelVl}&PrNm={PrNm}&PrCode={PrCode}&PrStr={PrStr}"
            f"&TmpTgt={TmpTgt}&SLevTgt={SLevTgt}&SpdTgt={SpdTgt}"
            f"&OptMsk1={OptMsk1}&OptMsk2={OptMsk2}&Lang=7&Stm={Stm}"
            f"&Dry=0&RecipeId=0&StartCheckUp=0&DispTestOn=0"
        )
        
        session = async_get_clientsession(hass)
        try:
            async with async_timeout.timeout(10):
                await session.get(url)
        except Exception as e:
            _LOGGER.error(f"Error starting washing: {e}")
        
        if delay_str != "Нет":
            await hass.services.async_call(
                "select", "select_option",
                {"entity_id": "select.bianca_delay_start", "option": "Нет"}
            )
    
    async def handle_stop_washing(call):
        """Handle stop washing service."""
        ip_address = entry.data[CONF_IP_ADDRESS]
        url = f"http://{ip_address}/http-write.json?encrypted=0&Write=1&StSt=0"
        session = async_get_clientsession(hass)
        try:
            async with async_timeout.timeout(10):
                await session.get(url)
        except Exception as e:
            _LOGGER.error(f"Error stopping washing: {e}")
    
    hass.services.async_register(DOMAIN, "start_washing", handle_start_washing)
    hass.services.async_register(DOMAIN, "stop_washing", handle_stop_washing)
    
    return True


async def async_register_assets(hass: HomeAssistant) -> None:
    """Register custom icons and dashboard strategy."""
    if hasattr(hass.data, "bianca_assets_registered"):
        return
    
    icons_path = hass.config.path(f"custom_components/{DOMAIN}/bianca-icons.js")
    if not os.path.exists(icons_path):
        return
    
    www_dir = hass.config.path("www/community/bianca")
    www_icons_path = hass.config.path("www/community/bianca/bianca-icons.js")
    version_file_path = hass.config.path("www/community/bianca/version.txt")
    
    manifest_path = hass.config.path(f"custom_components/{DOMAIN}/manifest.json")
    current_version = VERSION
    try:
        def read_manifest():
            with open(manifest_path, "r") as f:
                return json.load(f)
        manifest = await asyncio.to_thread(read_manifest)
        current_version = manifest.get("version", VERSION)
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
    
    machine_image_src = hass.config.path(f"custom_components/{DOMAIN}/original.png")
    machine_image_dest = hass.config.path("www/community/bianca/original.png")
    if os.path.exists(machine_image_src):
        try:
            if need_copy or not os.path.exists(machine_image_dest):
                await asyncio.to_thread(shutil.copy2, machine_image_src, machine_image_dest)
        except Exception:
            pass
    
    dashboard_js_src = hass.config.path(f"custom_components/{DOMAIN}/dashboard/bianca-dashboard.js")
    dashboard_js_dest = hass.config.path("www/community/bianca/bianca-dashboard.js")
    if os.path.exists(dashboard_js_src):
        try:
            if need_copy or not os.path.exists(dashboard_js_dest):
                os.makedirs(www_dir, exist_ok=True)
                await asyncio.to_thread(shutil.copy2, dashboard_js_src, dashboard_js_dest)
        except Exception:
            pass
    
    simple_js_src = hass.config.path(f"custom_components/{DOMAIN}/dashboard/bianca-simple.js")
    simple_js_dest = hass.config.path("www/community/bianca/bianca-simple.js")
    if os.path.exists(simple_js_src):
        try:
            if need_copy or not os.path.exists(simple_js_dest):
                os.makedirs(www_dir, exist_ok=True)
                await asyncio.to_thread(shutil.copy2, simple_js_src, simple_js_dest)
                _LOGGER.info("Copied bianca-simple.js to %s", simple_js_dest)
        except Exception as e:
            _LOGGER.error("Failed to copy bianca-simple.js: %s", e)
    
    admin_html_src = hass.config.path(f"custom_components/{DOMAIN}/admin.html")
    admin_html_dest = hass.config.path("www/community/bianca/admin.html")
    if os.path.exists(admin_html_src):
        try:
            if need_copy or not os.path.exists(admin_html_dest):
                os.makedirs(www_dir, exist_ok=True)
                await asyncio.to_thread(shutil.copy2, admin_html_src, admin_html_dest)
                _LOGGER.info("Copied admin HTML to %s", admin_html_dest)
        except Exception as e:
            _LOGGER.error("Failed to copy admin HTML: %s", e)
    
    # Регистрируем JS файлы
    if "bianca_assets_registered" not in hass.data:
        try:
            add_extra_js_url(hass, "/local/community/bianca/bianca-icons.js")
            add_extra_js_url(hass, "/local/community/bianca/bianca-dashboard.js")
            add_extra_js_url(hass, "/local/community/bianca/bianca-simple.js")
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
        if not self.device_available:
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
                                if self._last_valid_data is not None:
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
            if self.device_available and self._last_valid_data is not None:
                return self._last_valid_data
            raise UpdateFailed(f"Error fetching data: {e}")
