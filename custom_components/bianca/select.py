"""Select platform for Bianca integration - Version 2.4.3."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import CONF_IP_ADDRESS

from .const import DOMAIN, OPTION_TO_ENTITY
from .program_manager import ProgramManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca selects dynamically."""
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id]["async_add_entities"] = async_add_entities
    
    # Создаём ProgramManager через executor (блокирующий I/O)
    def create_program_manager():
        return ProgramManager(hass)
    program_manager = await hass.async_add_executor_job(create_program_manager)
    hass.data[DOMAIN][entry.entry_id]["program_manager"] = program_manager
    
    # Получаем первую программу для установки опций по умолчанию
    programs = program_manager.get_all_programs()
    if not programs:
        _LOGGER.error("No programs found in configuration")
        return
    
    default_program_id, default_program_name = programs[0]
    default_program = program_manager.get_program(default_program_id)
    
    program_select = BiancaProgramSelect(entry, hass, program_manager)
    
    selects = {}
    entities = [program_select]
    
    for option_key, entity_id in OPTION_TO_ENTITY.items():
        option_config = default_program.get("options", {}).get(option_key, {})
        values = option_config.get("values", ["Нет"])
        default_value = option_config.get("default", values[0] if values else "Нет")
        
        select = BiancaOptionSelect(
            entry, hass, program_manager, option_key, 
            values, default_value, entity_id
        )
        selects[option_key] = select
        entities.append(select)
    
    delay_start_select = BiancaDelayStartSelect(entry, hass)
    selects["delay_start"] = delay_start_select
    entities.append(delay_start_select)
    
    hass.data[DOMAIN][entry.entry_id]["selects"] = selects
    hass.data[DOMAIN][entry.entry_id]["program_select"] = program_select
    
    async_add_entities(entities)


class BiancaProgramSelect(SelectEntity):
    """Program selection that triggers update of all dependent selects."""

    def __init__(self, entry: ConfigEntry, hass: HomeAssistant, program_manager: ProgramManager):
        self._entry = entry
        self._hass = hass
        self._program_manager = program_manager
        self.entity_id = "select.bianca_program"
        self._attr_name = "Bianca Программа стирки"
        self._attr_unique_id = f"{entry.entry_id}_program"
        self._attr_icon = "mdi:washing-machine"
        self._attr_entity_category = EntityCategory.CONFIG
        
        programs = program_manager.get_all_programs()
        self._attr_options = [name for _, name in programs]
        self._program_map = {name: prog_id for prog_id, name in programs}
        self._attr_current_option = self._attr_options[0] if self._attr_options else None

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])}}

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        self.async_write_ha_state()
        
        program_id = self._program_map.get(option)
        if program_id:
            self._program_manager.current_program_id = program_id
            await self._update_all_selects(program_id)

    async def _update_all_selects(self, program_id: int):
        selects = self._hass.data[DOMAIN][self._entry.entry_id].get("selects", {})
        
        temp_select = selects.get("temperature")
        current_temperature = temp_select.current_option if temp_select else "60°C"
        context = {"temperature": current_temperature}
        
        skip_options = ["delay_start"]
        
        for option_key, select in selects.items():
            if option_key in skip_options:
                continue
            
            values = self._program_manager.get_option_values(program_id, option_key)
            default_value = self._program_manager.get_option_default(program_id, option_key)
            is_available = self._program_manager.is_option_available(program_id, option_key, context)
            
            if not is_available or not values or (len(values) == 1 and values[0] == "Нет"):
                select.update_options(["Нет"], "Нет", available=False)
            else:
                new_value = default_value if default_value in values else values[0]
                select.update_options(values, new_value, available=True)


class BiancaDelayStartSelect(SelectEntity):
    """Delay start selection - independent of program."""

    def __init__(self, entry: ConfigEntry, hass: HomeAssistant):
        self._entry = entry
        self._hass = hass
        self.entity_id = "select.bianca_delay_start"
        self._attr_name = "Bianca Отложенный старт"
        self._attr_unique_id = f"{entry.entry_id}_delay_start"
        self._attr_icon = "bianca:delay"
        self._attr_entity_category = EntityCategory.CONFIG
        
        self._attr_options = [
            "Нет", "30 мин", "1 час", "1 час 30 мин", "2 часа", "2 часа 30 мин",
            "3 часа", "3 часа 30 мин", "4 часа", "4 часа 30 мин", "5 часов", "5 часов 30 мин",
            "6 часов", "6 часов 30 мин", "7 часов", "7 часов 30 мин", "8 часов", "8 часов 30 мин",
            "9 часов", "9 часов 30 мин", "10 часов", "10 часов 30 мин", "11 часов", "11 часов 30 мин",
            "12 часов", "12 часов 30 мин", "13 часов", "13 часов 30 мин", "14 часов", "14 часов 30 мин",
            "15 часов", "15 часов 30 мин", "16 часов", "16 часов 30 мин", "17 часов", "17 часов 30 мин",
            "18 часов", "18 часов 30 мин", "19 часов", "19 часов 30 мин", "20 часов", "20 часов 30 мин",
            "21 час", "21 час 30 мин", "22 часа", "22 часа 30 мин", "23 часа", "23 часа 30 мин", "24 часа"
        ]
        self._attr_current_option = "Нет"

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])}}

    @property
    def available(self) -> bool:
        return True

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        self.async_write_ha_state()


class BiancaOptionSelect(SelectEntity):
    """Base class for Bianca option selects."""

    def __init__(
        self,
        entry: ConfigEntry,
        hass: HomeAssistant,
        program_manager: ProgramManager,
        option_key: str,
        options: list[str],
        default_option: str,
        entity_id: str,
    ):
        self._entry = entry
        self._hass = hass
        self._program_manager = program_manager
        self._option_key = option_key
        self.entity_id = entity_id
        self._attr_name = f"Bianca {self._get_option_name(option_key)}"
        self._attr_unique_id = f"{entry.entry_id}_{option_key}"
        self._attr_icon = self._get_option_icon(option_key)
        self._attr_options = options
        self._attr_current_option = default_option
        self._attr_entity_category = EntityCategory.CONFIG
        self._available = True

    def _get_option_name(self, option_key: str) -> str:
        names = {
            "temperature": "Температура стирки",
            "spin": "Скорость отжима",
            "soil": "Уровень загрязнения",
            "steam": "Пар",
            "pre_wash": "Предварительная стирка",
            "hygiene": "Гигиеническая стирка",
            "anti_crease": "Анти сминание",
            "night_spin": "Ночная стирка",
            "extra_rinse": "Дополнительные полоскания",
            "aqua_plus": "Акваплюс",
            "zoom": "Режим ZOOM",
        }
        return names.get(option_key, option_key)

    def _get_option_icon(self, option_key: str) -> str:
        icons = {
            "temperature": "mdi:thermometer",
            "spin": "bianca:spin",
            "soil": "bianca:duco-2",
            "steam": "bianca:steam",
            "pre_wash": "bianca:pre-wash",
            "hygiene": "bianca:hygiene-wash",
            "anti_crease": "bianca:anti-crease",
            "night_spin": "bianca:night-spin",
            "extra_rinse": "bianca:rinsing",
            "aqua_plus": "bianca:extra-water",
            "zoom": "bianca:zoom",
        }
        return icons.get(option_key, "mdi:help-circle")

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])}}

    @property
    def available(self) -> bool:
        return self._available

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        self.async_write_ha_state()
        
        program_id = self._program_manager.current_program_id
        if program_id:
            current_state = self._get_current_state()
            to_disable = self._program_manager.check_mutual_exclusion(
                program_id, self._option_key, option, current_state
            )
            
            for opt_key, new_value in to_disable.items():
                select = self._hass.data[DOMAIN][self._entry.entry_id].get("selects", {}).get(opt_key)
                if select and select.current_option != new_value:
                    await select.async_select_option(new_value)
        
        if self._option_key == "temperature" and program_id:
            await self._update_hygiene(program_id, option)

    def _get_current_state(self) -> dict:
        state = {}
        selects = self._hass.data[DOMAIN][self._entry.entry_id].get("selects", {})
        for opt_key, select in selects.items():
            if opt_key != "delay_start":
                state[opt_key] = select.current_option
        return state

    async def _update_hygiene(self, program_id: int, temperature: str):
        selects = self._hass.data[DOMAIN][self._entry.entry_id].get("selects", {})
        hygiene_select = selects.get("hygiene")
        
        if hygiene_select:
            context = {"temperature": temperature}
            is_available = self._program_manager.is_option_available(program_id, "hygiene", context)
            values = self._program_manager.get_option_values(program_id, "hygiene")
            default_value = self._program_manager.get_option_default(program_id, "hygiene")
            
            if not is_available or not values or (len(values) == 1 and values[0] == "Нет"):
                hygiene_select.update_options(["Нет"], "Нет", available=False)
            else:
                current = hygiene_select.current_option
                if current not in values:
                    current = default_value if default_value in values else values[0]
                hygiene_select.update_options(values, current, available=True)

    def update_options(self, options: list[str], current_option: str = None, available: bool = True):
        self._attr_options = options
        if current_option and current_option in options:
            self._attr_current_option = current_option
        elif self._attr_current_option not in options:
            self._attr_current_option = options[0] if options else "Нет"
        self._available = available
        self.async_write_ha_state()