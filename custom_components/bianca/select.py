"""Select platform for Bianca integration."""
from __future__ import annotations

import logging
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN
from . import BiancaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca selects."""
    coordinator: BiancaDataUpdateCoordinator = entry.runtime_data
    
    entities = [
        BiancaProgramSelect(coordinator, entry, hass),
        BiancaTemperatureSelect(coordinator, entry, hass),
        BiancaSpinSelect(coordinator, entry, hass),
        BiancaDelayStartSelect(coordinator, entry, hass),
        BiancaSoilSelect(coordinator, entry, hass),
        BiancaSteamSelect(coordinator, entry, hass),
        BiancaPreWashSelect(coordinator, entry, hass),
        BiancaHygieneSelect(coordinator, entry, hass),
        BiancaAntiCreaseSelect(coordinator, entry, hass),
        BiancaNightSpinSelect(coordinator, entry, hass),
        BiancaExtraRinseSelect(coordinator, entry, hass),
        BiancaAquaPlusSelect(coordinator, entry, hass),
        BiancaZoomSelect(coordinator, entry, hass),
    ]
    
    async_add_entities(entities)


class BiancaBaseSelect(CoordinatorEntity, SelectEntity):
    """Base class for Bianca selects."""

    def __init__(
        self,
        coordinator: BiancaDataUpdateCoordinator,
        entry: ConfigEntry,
        hass: HomeAssistant,
        entity_id_key: str,
        name: str,
        icon: str,
        options: list[str],
        current_option: str = None,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
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

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
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
        await super().async_select_option(option)
        await self._update_dependent_selects(option)

    async def _update_dependent_selects(self, program: str) -> None:
        """Update temperature, spin, soil and other selects based on program."""
        # Определяем доступные температуры
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

        # Определяем доступные обороты
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

        # Определяем доступные уровни загрязнения
        if program in ["Perfect 20°C"]:
            soil_options = ["Нормально"]
            default_soil = "Нормально"
        elif program in ["Шерсть", "Деликатная", "Полоскание", "Слив + Отжим", "Сохранить свежесть", "Perfect rapid 59 минут"]:
            soil_options = ["Нет"]
            default_soil = "Нет"
        else:
            soil_options = ["Нет", "Мало", "Нормально", "Очень"]
            default_soil = "Нет"

        # Обновляем температуру
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_temperature", "options": temp_options}
        )
        await self._hass.services.async_call(
            "input_select", "select_option",
            {"entity_id": "input_select.bianca_temperature", "option": default_temp}
        )

        # Обновляем обороты
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_spin", "options": spin_options}
        )
        await self._hass.services.async_call(
            "input_select", "select_option",
            {"entity_id": "input_select.bianca_spin", "option": default_spin}
        )

        # Обновляем уровень загрязнения
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_soil", "options": soil_options}
        )
        await self._hass.services.async_call(
            "input_select", "select_option",
            {"entity_id": "input_select.bianca_soil", "option": default_soil}
        )

        # Обновляем доступность опций
        await self._update_option_availability(program)
        
        # Обновляем взаимоисключающие опции
        await self._update_mutual_exclusive(program)

    async def _update_option_availability(self, program: str) -> None:
        """Update which options are available for the selected program."""
        
        # Steam available
        steam_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Perfect 20°C", "Деликатная"]
        steam_options = ["Без пара", "С паром"] if steam_available else ["Без пара"]
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_steam", "options": steam_options}
        )
        if not steam_available:
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_steam", "option": "Без пара"}
            )

        # Pre-wash available
        prewash_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани"]
        prewash_options = ["Нет", "Есть"] if prewash_available else ["Нет"]
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_pre_wash", "options": prewash_options}
        )
        if not prewash_available:
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_pre_wash", "option": "Нет"}
            )

        # Hygiene available (will be updated with temperature later)
        hygiene_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани"]
        if not hygiene_available:
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_hygiene", "options": ["Нет"]}
            )
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_hygiene", "option": "Нет"}
            )

        # Anti-crease available
        anticrease_available = program not in ["Хлопок: Интенсивная стирка", "Хлопок", "Полоскание", "Слив + Отжим", "Perfect rapid 59 минут", "Быстрая"]
        # Night spin available
        nightspin_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Шерсть", "Деликатная", "Perfect 20°C"]
        
        # For mutual exclusive programs, options will be handled separately
        mutual_exclusive = program in ["Синтетика и цветные ткани", "Шерсть", "Деликатная"]
        
        if mutual_exclusive:
            # Don't set options now, let mutual exclusive handler do it
            pass
        elif program in ["Хлопок: Интенсивная стирка", "Хлопок", "Perfect 20°C"]:
            # Only night spin available
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
            # Only anti-crease available
            anticrease_options = ["Нет", "Есть"] if anticrease_available else ["Нет"]
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_anti_crease", "options": anticrease_options}
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
            # Both options available (not mutual exclusive)
            anticrease_options = ["Нет", "Есть"] if anticrease_available else ["Нет"]
            night_options = ["Нет", "Есть"] if nightspin_available else ["Нет"]
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_anti_crease", "options": anticrease_options}
            )
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_night_spin", "options": night_options}
            )

        # Extra rinse available
        extra_rinse_available = program not in ["Perfect rapid 59 минут", "Быстрая", "Сохранить свежесть"]
        if not extra_rinse_available or program == "Полоскание":
            rinse_options = ["Нет"]
        elif program == "Шерсть":
            rinse_options = ["Нет", "1 полоскание"]
        else:
            rinse_options = ["Нет", "1 полоскание", "2 полоскания", "3 полоскания"]
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_extra_rinse", "options": rinse_options}
        )
        if program == "Полоскание":
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_extra_rinse", "option": "Нет"}
            )

        # Aqua plus available
        aquaplus_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Perfect 20°C"]
        aquaplus_options = ["Нет", "Есть"] if aquaplus_available else ["Нет"]
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_aqua_plus", "options": aquaplus_options}
        )
        if not aquaplus_available:
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_aqua_plus", "option": "Нет"}
            )

        # Zoom available
        zoom_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Шерсть", "Perfect rapid 59 минут", "Деликатная"]
        zoom_options = ["Нет", "Есть"] if zoom_available else ["Нет"]
        await self._hass.services.async_call(
            "input_select", "set_options",
            {"entity_id": "input_select.bianca_zoom", "options": zoom_options}
        )
        if not zoom_available:
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_zoom", "option": "Нет"}
            )

    async def _update_mutual_exclusive(self, program: str) -> None:
        """Update mutual exclusive options (anti-crease vs night spin)."""
        mutual_exclusive = program in ["Синтетика и цветные ткани", "Шерсть", "Деликатная"]
        
        if not mutual_exclusive:
            return
        
        anticrease_current = self._hass.states.get("input_select.bianca_anti_crease")
        nightspin_current = self._hass.states.get("input_select.bianca_night_spin")
        
        anticrease_val = anticrease_current.state if anticrease_current else "Нет"
        nightspin_val = nightspin_current.state if nightspin_current else "Нет"
        
        if anticrease_val == "Есть" and nightspin_val == "Есть":
            # Both selected - need to resolve conflict
            # Default to night spin (more common preference)
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_anti_crease", "options": ["Нет", "Есть"]}
            )
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_anti_crease", "option": "Нет"}
            )
            night_options = ["Нет", "Есть"]
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_night_spin", "options": night_options}
            )
        else:
            # Normal case - both available
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_anti_crease", "options": ["Нет", "Есть"]}
            )
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_night_spin", "options": ["Нет", "Есть"]}
            )


class BiancaTemperatureSelect(BiancaBaseSelect):
    """Temperature selection that triggers hygiene update."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "temperature", "Температура стирки", "mdi:thermometer",
            ["0°C", "20°C", "30°C", "40°C", "60°C", "90°C"]
        )

    async def async_select_option(self, option: str) -> None:
        """Update temperature and check hygiene availability."""
        await super().async_select_option(option)
        await self._update_hygiene_availability(option)

    async def _update_hygiene_availability(self, temperature: str) -> None:
        """Update hygiene option based on temperature."""
        program_select = self._hass.states.get("input_select.bianca_program")
        if not program_select:
            return
        
        program = program_select.state
        hygiene_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани"]
        temp_high = temperature in ["60°C", "90°C"]
        
        if hygiene_available and temp_high:
            hygiene_options = ["Нет", "Есть"]
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_hygiene", "options": hygiene_options}
            )
        elif hygiene_available:
            await self._hass.services.async_call(
                "input_select", "set_options",
                {"entity_id": "input_select.bianca_hygiene", "options": ["Нет"]}
            )
            await self._hass.services.async_call(
                "input_select", "select_option",
                {"entity_id": "input_select.bianca_hygiene", "option": "Нет"}
            )


class BiancaSpinSelect(BiancaBaseSelect):
    """Spin speed selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "spin", "Скорость отжима", "mdi:rotate-right",
            ["0 об/мин", "400 об/мин", "500 об/мин", "600 об/мин", "700 об/мин",
             "800 об/мин", "900 об/мин", "1000 об/мин", "1100 об/мин", "1200 об/мин",
             "1300 об/мин", "1400 об/мин"]
        )


class BiancaDelayStartSelect(BiancaBaseSelect):
    """Delay start selection."""

    def __init__(self, coordinator, entry, hass):
        options = ["Нет", "30 мин", "1 час", "1 час 30 мин", "2 часа", "2 часа 30 мин",
                   "3 часа", "3 часа 30 мин", "4 часа", "4 час 30 мин", "5 часов", "5 часов 30 мин",
                   "6 часов", "6 часов 30 мин", "7 часов", "7 часов 30 мин", "8 часов", "8 часов 30 мин",
                   "9 часов", "9 часов 30 мин", "10 часов", "10 часов 30 мин", "11 часов", "11 часов 30 мин",
                   "12 часов", "12 часов 30 мин", "13 часов", "13 часов 30 мин", "14 часов", "14 часов 30 мин",
                   "15 часов", "15 часов 30 мин", "16 часов", "16 часов 30 мин", "17 часов", "17 часов 30 мин",
                   "18 часов", "18 часов 30 мин", "19 часов", "19 часов 30 мин", "20 часов", "20 часов 30 мин",
                   "21 час", "21 час 30 мин", "22 часа", "22 часа 30 мин", "23 часа", "23 часа 30 мин", "24 часа"]
        super().__init__(
            coordinator, entry, hass,
            "delay_start", "Отложенный старт", "mdi:timer-outline",
            options
        )


class BiancaSoilSelect(BiancaBaseSelect):
    """Soil level selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "soil", "Уровень загрязнения", "mdi:water-percent",
            ["Нет", "Мало", "Нормально", "Очень"]
        )


class BiancaSteamSelect(BiancaBaseSelect):
    """Steam selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "steam", "Пар", "mdi:water-vapor",
            ["Без пара", "С паром"]
        )


class BiancaPreWashSelect(BiancaBaseSelect):
    """Pre-wash selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "pre_wash", "Предварительная стирка", "mdi:soap",
            ["Нет", "Есть"]
        )


class BiancaHygieneSelect(BiancaBaseSelect):
    """Hygiene wash selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "hygiene", "Гигиеническая стирка", "mdi:sterling",
            ["Нет", "Есть"]
        )


class BiancaAntiCreaseSelect(BiancaBaseSelect):
    """Anti-crease selection with mutual exclusion."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "anti_crease", "Анти сминание", "mdi:iron",
            ["Нет", "Есть"]
        )

    async def async_select_option(self, option: str) -> None:
        """Update anti-crease and handle mutual exclusion."""
        await super().async_select_option(option)
        
        if option == "Есть":
            # If anti-crease is ON, turn OFF night spin
            night_spin = self._hass.states.get("input_select.bianca_night_spin")
            if night_spin and night_spin.state == "Есть":
                await self._hass.services.async_call(
                    "input_select", "select_option",
                    {"entity_id": "input_select.bianca_night_spin", "option": "Нет"}
                )


class BiancaNightSpinSelect(BiancaBaseSelect):
    """Night spin selection with mutual exclusion."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "night_spin", "Ночной отжим", "mdi:weather-night",
            ["Нет", "Есть"]
        )

    async def async_select_option(self, option: str) -> None:
        """Update night spin and handle mutual exclusion."""
        await super().async_select_option(option)
        
        if option == "Есть":
            # If night spin is ON, turn OFF anti-crease
            anti_crease = self._hass.states.get("input_select.bianca_anti_crease")
            if anti_crease and anti_crease.state == "Есть":
                await self._hass.services.async_call(
                    "input_select", "select_option",
                    {"entity_id": "input_select.bianca_anti_crease", "option": "Нет"}
                )


class BiancaExtraRinseSelect(BiancaBaseSelect):
    """Extra rinse selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "extra_rinse", "Дополнительные полоскания", "mdi:water",
            ["Нет", "1 полоскание", "2 полоскания", "3 полоскания"]
        )


class BiancaAquaPlusSelect(BiancaBaseSelect):
    """Aqua plus selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "aqua_plus", "Акваплюс", "mdi:water-plus",
            ["Нет", "Есть"]
        )


class BiancaZoomSelect(BiancaBaseSelect):
    """Zoom mode selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "zoom", "Режим ZOOM", "mdi:arrow-expand-all",
            ["Нет", "Есть"]
        )
