"""Services for Bianca integration."""

import json
import logging
import async_timeout
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import HomeAssistant

from .const import DOMAIN, OPTION_VALUE_TO_CODE

_LOGGER = logging.getLogger(__name__)


async def async_register_services(hass: HomeAssistant, program_manager):
    """Register services for Bianca."""
    
    async def send_command(hass, entry_id, ip_address, url):
        """Отправляет команду и записывает ответ в сенсор."""
        coordinator = hass.data[DOMAIN][entry_id]["coordinator"]
        session = async_get_clientsession(hass)
        
        try:
            async with async_timeout.timeout(10):
                async with session.get(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        try:
                            data = json.loads(text)
                            coordinator.set_write_status(data.get("response", "NO_RESPONSE_FIELD"))
                        except json.JSONDecodeError:
                            coordinator.set_write_status("PARSE ERROR")
                    else:
                        coordinator.set_write_status(f"HTTP {response.status}")
        except Exception:
            coordinator.set_write_status("CONNECTION ERROR")
    
    async def handle_start_washing(call):
        """Handle start washing service."""
        
        # Получаем entry_id
        entry_id = None
        for entry in hass.config_entries.async_entries(DOMAIN):
            entry_id = entry.entry_id
            break
        
        if not entry_id:
            _LOGGER.error("No Bianca integration found")
            return
        
        # Сохраняем user_id из контекста
        user_id = call.context.user_id
        if user_id and DOMAIN in hass.data and entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN][entry_id]["started_by_user"] = user_id
            _LOGGER.debug(f"Washing started by user_id: {user_id}")
        
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
            coordinator = hass.data[DOMAIN][entry_id]["coordinator"]
            coordinator.set_write_status(f"UNKNOWN PROGRAM: {program_name}")
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
            "3 часа": 6, "3 часа 30 мин": 7, "4 часа": 8, "4 часа 30 мин": 9, "5 часов": 10,
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
        
        ip_address = None
        for entry in hass.config_entries.async_entries(DOMAIN):
            ip_address = entry.data.get("ip_address")
            break
        
        if not ip_address:
            _LOGGER.error("No Bianca integration found")
            return
        
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
        
        await send_command(hass, entry_id, ip_address, url)
        
        if delay_str != "Нет":
            await hass.services.async_call(
                "select", "select_option",
                {"entity_id": "select.bianca_delay_start", "option": "Нет"}
            )
    
    async def handle_stop_washing(call):
        """Handle stop washing service."""
        entry_id = None
        for entry in hass.config_entries.async_entries(DOMAIN):
            entry_id = entry.entry_id
            break
        
        if not entry_id:
            _LOGGER.error("No Bianca integration found")
            return
        
        ip_address = None
        for entry in hass.config_entries.async_entries(DOMAIN):
            ip_address = entry.data.get("ip_address")
            break
        
        if not ip_address:
            _LOGGER.error("No Bianca integration found")
            return
        
        url = f"http://{ip_address}/http-write.json?encrypted=0&Write=1&StSt=0"
        
        await send_command(hass, entry_id, ip_address, url)
    
    hass.services.async_register("bianca", "start_washing", handle_start_washing)
    hass.services.async_register("bianca", "stop_washing", handle_stop_washing)
    _LOGGER.info("Bianca services registered")
