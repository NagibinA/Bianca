"""Select platform for Bianca integration - Version 2.0.0."""

from __future__ import annotations

import logging
from typing import Any

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
    
    # Сохраняем коллбэк для динамического добавления
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id]["async_add_entities"] = async_add_entities
    
    # Инициализируем ProgramManager
    program_manager = ProgramManager(hass)
    hass.data[DOMAIN][entry.entry_id]["program_manager"] = program_manager
    
    # Получаем ID программы по умолчанию (1 = Хлопок: Интенсивная)
    default_program_id = "1"
    default_program = program_manager.get_program(default_program_id)
    
    if not default_program:
        _LOGGER.error("Failed to load default program configuration")
        return
    
    # Создаём селект программы
    program_select = BiancaProgramSelect(entry, hass, program_manager)
    
    # Создаём все зависимые селекты
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
    
    # Создаём селект отложенного старта (не зависит от программы)
    delay_start_select = BiancaDelayStartSelect(entry, hass)
    selects["delay_start"] = delay_start_select
    entities.append(delay_start_select)
    
    # Сохраняем ссылки на селекты
    hass.data[DOMAIN][entry.entry_id]["selects"] = selects
    hass.data[DOMAIN][entry.entry_id]["program_select"] = program_select
    
    async_add_entities(entities)


class BiancaProgramSelect(SelectEntity):
    """Program selection that triggers update of all dependent selects."""

    def __init__(self, entry: ConfigEntry, hass: HomeAssistant, program_manager: ProgramManager):
        """Initialize the program select."""
        self._entry = entry
        self._hass = hass
        self._program_manager = program_manager
        self.entity_id = "select.bianca_program"
        self._attr_name = "Bianca Программа стирки"
        self._attr_unique_id = f"{entry.entry_id}_program"
        self._attr_icon = "mdi:washing-machine"
        self._attr_entity_category = EntityCategory.CONFIG
        
        # Список программ
        programs = program_manager.get_all_programs()
        self._attr_options = [name for _, name in programs]
        self._program_map = {name: pid for pid, name in programs}
        self._attr_current_option = self._attr_options[0] if self._attr_options else None

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])},
        }

    async def async_select_option(self, option: str) -> None:
        """Update current option and update all dependent selects."""
        self._attr_current_option = option
        self.async_write_ha_state()
        
        program_id = self._program_map.get(option)
        if program_id:
            self._program_manager.current_program = program_id
            await self._update_all_selects(program_id)

    async def _update_all_selects(self, program_id: str):
        """Update all option selects when program changes."""
        selects = self._hass.data[DOMAIN][self._entry.entry_id].get("selects", {})
        
        # Получаем текущую температуру для проверки зависимостей
        temp_select = self._hass.states.get("select.bianca_temperature")
        current_temperature = temp_select.state if temp_select else "60°C"
        
        context = {"temperature": current_temperature}
        
        # Селекты, которые не зависят от программы (отложенный старт)
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
                current = select.current_option
                if current not in values:
                    current = default_value if default_value in values else values[0]
                select.update_options(values, current, available=True)


class BiancaDelayStartSelect(SelectEntity):
    """Delay start selection - independent of program."""

    def __init__(self, entry: ConfigEntry, hass: HomeAssistant):
        """Initialize the delay start select."""
        self._entry = entry
        self._hass = hass
        self.entity_id = "select.bianca_delay_start"
        self._attr_name = "Bianca Отложенный старт"
        self._attr_unique_id = f"{entry.entry_id}_delay_start"
        self._attr_icon = "mdi:timer-outline"
        self._attr_entity_category = EntityCategory.CONFIG
        
        self._attr_options = [
            "Нет", "30 мин", "1 час", "1 час 30 мин", "2 часа", "2 часа 30 мин",
            "3 часа", "3 часа 30 мин", "4 часа", "4 час 30 мин", "5 часов", "5 часов 30 мин",
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
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])},
        }

    @property
    def available(self) -> bool:
        """Delay start is always available."""
        return True

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
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
        """Initialize the option select."""
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
        """Get display name for option."""
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
        """Get icon for option."""
        icons = {
            "temperature": "mdi:thermometer",
            "spin": "mdi:rotate-right",
            "soil": "mdi:water-percent",
            "steam": "mdi:water-vapor",
            "pre_wash": "mdi:soap",
            "hygiene": "mdi:sterling",
            "anti_crease": "mdi:iron",
            "night_spin": "mdi:weather-night",
            "extra_rinse": "mdi:water",
            "aqua_plus": "mdi:water-plus",
            "zoom": "mdi:arrow-expand-all",
        }
        return icons.get(option_key, "mdi:help-circle")

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])},
        }

    @property
    def available(self) -> bool:
        """Return if select is available."""
        return self._available

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()
        
        # Проверяем взаимные исключения
        program_id = self._program_manager.current_program
        if program_id:
            current_state = self._get_current_state()
            to_disable = self._program_manager.check_mutual_exclusion(
                program_id, self._option_key, option, current_state
            )
            
            for opt_key, new_value in to_disable.items():
                select = self._hass.data[DOMAIN][self._entry.entry_id].get("selects", {}).get(opt_key)
                if select and select.current_option != new_value:
                    await select.async_select_option(new_value)
        
        # Если изменилась температура, обновляем гигиену
        if self._option_key == "temperature" and program_id:
            await self._update_hygiene(program_id, option)

    def _get_current_state(self) -> dict:
        """Get current state of all option selects."""
        state = {}
        selects = self._hass.data[DOMAIN][self._entry.entry_id].get("selects", {})
        for opt_key, select in selects.items():
            if opt_key != "delay_start":  # delay_start не входит в опции
                state[opt_key] = select.current_option
        return state

    async def _update_hygiene(self, program_id: str, temperature: str):
        """Update hygiene options when temperature changes."""
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
        """Update available options dynamically."""
        self._attr_options = options
        if current_option and current_option in options:
            self._attr_current_option = current_option
        elif self._attr_current_option not in options:
            self._attr_current_option = options[0] if options else "Нет"
        self._available = available
        self.async_write_ha_state()
