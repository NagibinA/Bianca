"""Input select platform for Bianca integration."""
from __future__ import annotations

import logging
from homeassistant.components.input_select import InputSelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import CONF_IP_ADDRESS

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca input selects."""
    
    entities = [
        BiancaProgramSelect(entry, hass),
        BiancaTemperatureSelect(entry, hass),
        BiancaSpinSelect(entry, hass),
        BiancaDelayStartSelect(entry, hass),
        BiancaSoilSelect(entry, hass),
        BiancaSteamSelect(entry, hass),
        BiancaPreWashSelect(entry, hass),
        BiancaHygieneSelect(entry, hass),
        BiancaAntiCreaseSelect(entry, hass),
        BiancaNightSpinSelect(entry, hass),
        BiancaExtraRinseSelect(entry, hass),
        BiancaAquaPlusSelect(entry, hass),
        BiancaZoomSelect(entry, hass),
    ]
    
    async_add_entities(entities)


class BiancaBaseSelect(InputSelectEntity):
    """Base class for Bianca input selects."""

    def __init__(
        self,
        entry: ConfigEntry,
        hass: HomeAssistant,
        entity_id_key: str,
        name: str,
        icon: str,
        options: list[str],
        current_option: str = None,
    ) -> None:
        """Initialize the select."""
        self._entry = entry
        self._hass = hass
        self.entity_id = f"input_select.bianca_{entity_id_key}"
        self._attr_name = f"Bianca {name}"
        self._attr_unique_id = f"{entry.entry_id}_{entity_id_key}"
        self._attr_icon = icon
        self._attr_options = options
        self._attr_current_option = current_option or options[0]
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])},
        }

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()


class BiancaProgramSelect(BiancaBaseSelect):
    """Program selection with dynamic updates."""

    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "program", "Программа стирки", "mdi:washing-machine",
            [
                "Хлопок: Интенсивная стирка",
                "Хлопок",
                "Синтетика и цветные ткани",
                "Шерсть",
                "Деликатная",
                "Perfect 20°C",
                "Полоскание",
                "Слив + Отжим",
                "Сохранить свежесть",
                "Perfect rapid 59 минут",
                "Быстрая"
            ]
        )

    async def async_select_option(self, option: str) -> None:
        """Update current option and trigger updates for dependent selects."""
        _LOGGER.info(f"Program selected: {option}")
        await super().async_select_option(option)
        await self._update_dependent_selects(option)

    async def _update_dependent_selects(self, program: str) -> None:
        """Update temperature, spin, soil and other selects using services."""
        _LOGGER.info(f"Updating dependent selects for program: {program}")
        
        # ========== TEMPERATURE OPTIONS ==========
        if program in ["Полоскание", "Слив + Отжим"]:
            temp_options = ["0°C"]
            default_temp = "0°C"
        elif program == "Perfect 20°C":
            temp_options = ["0°C", "20°C"]
            default_temp = "20°C"
        elif program in ["Шерсть", "Деликатная", "Сохранить свежесть"]:
            temp_options = ["0°C", "20°C", "30°C", "40°C"]
            default_temp = "30°C" if program in ["Шерсть", "Деликатная"] else "20°C"
        elif program in ["Быстрая", "Perfect rapid 59 минут"]:
            temp_options = ["0°C", "20°C", "30°C", "40°C", "60°C"]
            default_temp = "40°C"
        elif program in ["Хлопок", "Синтетика и цветные ткани"]:
            temp_options = ["0°C", "20°C", "30°C", "40°C", "60°C"]
            default_temp = "40°C"
        elif program in ["Хлопок: Интенсивная стирка"]:
            temp_options = ["0°C", "20°C", "30°C", "40°C", "60°C", "90°C"]
            default_temp = "60°C"
        else:
            temp_options = ["0°C", "20°C", "30°C", "40°C"]
            default_temp = "30°C"

        # ========== SPIN OPTIONS ==========
        if program in ["Шерсть"]:
            spin_options = ["0 об/мин", "400 об/мин", "500 об/мин", "600 об/мин", "700 об/мин", "800 об/мин"]
            default_spin = "800 об/мин"
        elif program == "Сохранить свежесть":
            spin_options = ["0 об/мин", "400 об/мин", "600 об/мин", "800 об/мин"]
            default_spin = "800 об/мин"
        elif program == "Деликатная":
            spin_options = ["0 об/мин", "400 об/мин"]
            default_spin = "400 об/мин"
        elif program in ["Perfect rapid 59 минут", "Полоскание"]:
            spin_options = ["0 об/мин", "400 об/мин", "500 об/мин", "600 об/мин", "700 об/мин", "800 об/мин", "900 об/мин", "1000 об/мин"]
            default_spin = "1000 об/мин"
        else:
            spin_options = ["0 об/мин", "400 об/мин", "600 об/мин", "700 об/мин", "800 об/мин", "900 об/мин", "1000 об/мин", "1100 об/мин", "1200 об/мин", "1300 об/мин", "1400 об/мин"]
            default_spin = "1000 об/мин"

        # ========== SOIL OPTIONS ==========
        if program in ["Perfect 20°C"]:
            soil_options = ["Нормально"]
            default_soil = "Нормально"
        elif program in ["Шерсть", "Деликатная", "Полоскание", "Слив + Отжим", "Сохранить свежесть", "Perfect rapid 59 минут"]:
            soil_options = ["Нет"]
            default_soil = "Нет"
        else:
            soil_options = ["Нет", "Мало", "Нормально", "Очень"]
            default_soil = "Нет"

        # ========== STEAM ==========
        steam_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Perfect 20°C", "Деликатная"]
        steam_options = ["Без пара", "С паром"] if steam_available else ["Без пара"]
        
        # ========== PRE-WASH ==========
        prewash_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани"]
        prewash_options = ["Нет", "Есть"] if prewash_available else ["Нет"]
        
        # ========== HYGIENE ==========
        hygiene_available_program = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани"]
        current_temp = self._hass.states.get("input_select.bianca_temperature")
        current_temp_value = current_temp.state if current_temp else "0°C"
        temp_high = current_temp_value in ["60°C", "90°C"]
        
        # ========== ANTI-CREASE & NIGHT SPIN ==========
        anticrease_available = program not in ["Хлопок: Интенсивная стирка", "Хлопок", "Полоскание", "Слив + Отжим", "Perfect rapid 59 минут", "Быстрая"]
        nightspin_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Шерсть", "Деликатная", "Perfect 20°C"]
        mutual_exclusive = program in ["Синтетика и цветные ткани", "Шерсть", "Деликатная"]
        
        # ========== EXTRA RINSE ==========
        extra_rinse_available = program not in ["Perfect rapid 59 минут", "Быстрая", "Сохранить свежесть"]
        if not extra_rinse_available or program == "Полоскание":
            rinse_options = ["Нет"]
        elif program == "Шерсть":
            rinse_options = ["Нет", "1 полоскание"]
        else:
            rinse_options = ["Нет", "1 полоскание", "2 полоскания", "3 полоскания"]
        
        # ========== AQUA PLUS ==========
        aquaplus_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Perfect 20°C"]
        aquaplus_options = ["Нет", "Есть"] if aquaplus_available else ["Нет"]
        
        # ========== ZOOM ==========
        zoom_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Шерсть", "Perfect rapid 59 минут", "Деликатная"]
        zoom_options = ["Нет", "Есть"] if zoom_available else ["Нет"]
        
        # ========== APPLY UPDATES USING SERVICES ==========
        
        # Update temperature
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_temperature", "options": temp_options}
        )
        await self._hass.services.async_call(
            "input_select", "select_option",
            {"entity_id": "input_select.bianca_temperature", "option": default_temp}
        )
        
        # Update spin
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_spin", "options": spin_options}
        )
        await self._hass.services.async_call(
            "input_select", "select_option",
            {"entity_id": "input_select.bianca_spin", "option": default_spin}
        )
        
        # Update soil
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_soil", "options": soil_options}
        )
        await self._hass.services.async_call(
            "input_select", "select_option",
            {"entity_id": "input_select.bianca_soil", "option": default_soil}
        )
        
        # Update steam
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_steam", "options": steam_options}
        )
        if not steam_available:
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_steam", "option": "Без пара"}
            )
        
        # Update pre-wash
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_pre_wash", "options": prewash_options}
        )
        if not prewash_available:
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_pre_wash", "option": "Нет"}
            )
        
        # Update hygiene (based on program and temperature)
        if hygiene_available_program and temp_high:
            hygiene_options_list = ["Нет", "Есть"]
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_hygiene", "options": hygiene_options_list}
            )
        elif hygiene_available_program:
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_hygiene", "options": ["Нет"]}
            )
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_hygiene", "option": "Нет"}
            )
        else:
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_hygiene", "options": ["Нет"]}
            )
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_hygiene", "option": "Нет"}
            )
        
        # Update anti-crease and night spin
        if mutual_exclusive:
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_anti_crease", "options": ["Нет", "Есть"]}
            )
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_night_spin", "options": ["Нет", "Есть"]}
            )
        elif program in ["Хлопок: Интенсивная стирка", "Хлопок", "Perfect 20°C"]:
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_anti_crease", "options": ["Нет"]}
            )
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_anti_crease", "option": "Нет"}
            )
            night_options = ["Нет", "Есть"] if nightspin_available else ["Нет"]
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_night_spin", "options": night_options}
            )
        elif anticrease_available and not nightspin_available:
            anticrease_options_list = ["Нет", "Есть"] if anticrease_available else ["Нет"]
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_anti_crease", "options": anticrease_options_list}
            )
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_night_spin", "options": ["Нет"]}
            )
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_night_spin", "option": "Нет"}
            )
        else:
            anticrease_options_list = ["Нет", "Есть"] if anticrease_available else ["Нет"]
            night_options = ["Нет", "Есть"] if nightspin_available else ["Нет"]
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_anti_crease", "options": anticrease_options_list}
            )
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_night_spin", "options": night_options}
            )
        
        # Update extra rinse
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_extra_rinse", "options": rinse_options}
        )
        if program == "Полоскание":
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_extra_rinse", "option": "Нет"}
            )
        
        # Update aqua plus
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_aqua_plus", "options": aquaplus_options}
        )
        if not aquaplus_available:
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_aqua_plus", "option": "Нет"}
            )
        
        # Update zoom
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_zoom", "options": zoom_options}
        )
        if not zoom_available:
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_zoom", "option": "Нет"}
            )


class BiancaTemperatureSelect(BiancaBaseSelect):
    """Temperature selection with hygiene update."""

    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "temperature", "Температура стирки", "mdi:thermometer",
            ["0°C", "20°C", "30°C", "40°C", "60°C", "90°C"]
        )

    async def async_select_option(self, option: str) -> None:
        """Update temperature and trigger hygiene update."""
        _LOGGER.info(f"Temperature selected: {option}")
        await super().async_select_option(option)
        
        # Get current program
        program_select = self._hass.states.get("input_select.bianca_program")
        if not program_select:
            return
        
        program = program_select.state
        hygiene_available_program = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани"]
        temp_high = option in ["60°C", "90°C"]
        
        if hygiene_available_program and temp_high:
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_hygiene", "options": ["Нет", "Есть"]}
            )
        elif hygiene_available_program:
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_hygiene", "options": ["Нет"]}
            )
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_hygiene", "option": "Нет"}
            )


class BiancaAntiCreaseSelect(BiancaBaseSelect):
    """Anti-crease selection with mutual exclusion."""

    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "anti_crease", "Анти сминание", "mdi:iron",
            ["Нет", "Есть"]
        )

    async def async_select_option(self, option: str) -> None:
        """Update anti-crease and handle mutual exclusion."""
        _LOGGER.info(f"Anti-crease selected: {option}")
        await super().async_select_option(option)
        
        if option == "Есть":
            night_spin = self._hass.states.get("input_select.bianca_night_spin")
            if night_spin and night_spin.state == "Есть":
                await self._hass.services.async_call(
                    "input_select", "select_option",
                    {"entity_id": "input_select.bianca_night_spin", "option": "Нет"}
                )


class BiancaNightSpinSelect(BiancaBaseSelect):
    """Night spin selection with mutual exclusion."""

    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "night_spin", "Ночной отжим", "mdi:weather-night",
            ["Нет", "Есть"]
        )

    async def async_select_option(self, option: str) -> None:
        """Update night spin and handle mutual exclusion."""
        _LOGGER.info(f"Night spin selected: {option}")
        await super().async_select_option(option)
        
        if option == "Есть":
            anti_crease = self._hass.states.get("input_select.bianca_anti_crease")
            if anti_crease and anti_crease.state == "Есть":
                await self._hass.services.async_call(
                    "input_select", "select_option",
                    {"entity_id": "input_select.bianca_anti_crease", "option": "Нет"}
                )


# ========== REMAINING SELECTS ==========

class BiancaSpinSelect(BiancaBaseSelect):
    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "spin", "Скорость отжима", "mdi:rotate-right",
            ["0 об/мин", "400 об/мин", "500 об/мин", "600 об/мин", "700 об/мин",
             "800 об/мин", "900 об/мин", "1000 об/мин", "1100 об/мин", "1200 об/мин",
             "1300 об/мин", "1400 об/мин"]
        )


class BiancaDelayStartSelect(BiancaBaseSelect):
    def __init__(self, entry, hass):
        options = ["Нет", "30 мин", "1 час", "1 час 30 мин", "2 часа", "2 часа 30 мин",
                   "3 часа", "3 часа 30 мин", "4 часа", "4 час 30 мин", "5 часов", "5 часов 30 мин",
                   "6 часов", "6 часов 30 мин", "7 часов", "7 часов 30 мин", "8 часов", "8 часов 30 мин",
                   "9 часов", "9 часов 30 мин", "10 часов", "10 часов 30 мин", "11 часов", "11 часов 30 мин",
                   "12 часов", "12 часов 30 мин", "13 часов", "13 часов 30 мин", "14 часов", "14 часов 30 мин",
                   "15 часов", "15 часов 30 мин", "16 часов", "16 часов 30 мин", "17 часов", "17 часов 30 мин",
                   "18 часов", "18 часов 30 мин", "19 часов", "19 часов 30 мин", "20 часов", "20 часов 30 мин",
                   "21 час", "21 час 30 мин", "22 часа", "22 часа 30 мин", "23 часа", "23 часа 30 мин", "24 часа"]
        super().__init__(
            entry, hass,
            "delay_start", "Отложенный старт", "mdi:timer-outline", options
        )


class BiancaSoilSelect(BiancaBaseSelect):
    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "soil", "Уровень загрязнения", "mdi:water-percent",
            ["Нет", "Мало", "Нормально", "Очень"]
        )


class BiancaSteamSelect(BiancaBaseSelect):
    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "steam", "Пар", "mdi:water-vapor",
            ["Без пара", "С паром"]
        )


class BiancaPreWashSelect(BiancaBaseSelect):
    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "pre_wash", "Предварительная стирка", "mdi:soap",
            ["Нет", "Есть"]
        )


class BiancaHygieneSelect(BiancaBaseSelect):
    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "hygiene", "Гигиеническая стирка", "mdi:sterling",
            ["Нет", "Есть"]
        )


class BiancaExtraRinseSelect(BiancaBaseSelect):
    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "extra_rinse", "Дополнительные полоскания", "mdi:water",
            ["Нет", "1 полоскание", "2 полоскания", "3 полоскания"]
        )


class BiancaAquaPlusSelect(BiancaBaseSelect):
    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "aqua_plus", "Акваплюс", "mdi:water-plus",
            ["Нет", "Есть"]
        )


class BiancaZoomSelect(BiancaBaseSelect):
    def __init__(self, entry, hass):
        super().__init__(
            entry, hass,
            "zoom", "Режим ZOOM", "mdi:arrow-expand-all",
            ["Нет", "Есть"]
        )
