"""Input select platform for Bianca integration."""
from __future__ import annotations

import logging
from homeassistant.components.input_select import InputSelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_IP_ADDRESS

from .const import DOMAIN
from . import BiancaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca input selects."""
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
    
    # Store references to selects for dynamic updates
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if entry.entry_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN][entry.entry_id]["selects"] = entities


class BiancaBaseSelect(CoordinatorEntity, InputSelectEntity):
    """Base class for Bianca input selects."""

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
        self._attr_unique_id = f"{entry.entry_id}_{entity_id_key}"
        self._attr_name = f"Bianca {name}"
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
    
    async def async_update_options(self, options: list[str], current_option: str = None) -> None:
        """Update available options dynamically."""
        self._attr_options = options
        if current_option and current_option in options:
            self._attr_current_option = current_option
        elif self._attr_current_option not in options:
            self._attr_current_option = options[0]
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
        _LOGGER.info(f"Program selected: {option}")
        await super().async_select_option(option)
        await self._update_dependent_selects(option)

    async def _update_dependent_selects(self, program: str) -> None:
        """Update temperature, spin, soil and other selects based on program."""
        _LOGGER.info(f"Updating dependent selects for program: {program}")
        
        # Get selects from storage
        selects = self._hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {}).get("selects", [])
        select_map = {s.entity_id: s for s in selects}
        
        # Define temperature options
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

        # Define spin options
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

        # Define soil options
        if program in ["Perfect 20°C"]:
            soil_options = ["Нормально"]
            default_soil = "Нормально"
        elif program in ["Шерсть", "Деликатная", "Полоскание", "Слив + Отжим", "Сохранить свежесть", "Perfect rapid 59 минут"]:
            soil_options = ["Нет"]
            default_soil = "Нет"
        else:
            soil_options = ["Нет", "Мало", "Нормально", "Очень"]
            default_soil = "Нет"

        # Update temperature
        if "input_select.bianca_temperature" in select_map:
            await select_map["input_select.bianca_temperature"].async_update_options(temp_options, default_temp)
        
        # Update spin
        if "input_select.bianca_spin" in select_map:
            await select_map["input_select.bianca_spin"].async_update_options(spin_options, default_spin)
        
        # Update soil
        if "input_select.bianca_soil" in select_map:
            await select_map["input_select.bianca_soil"].async_update_options(soil_options, default_soil)

        # Update option availability
        await self._update_option_availability(program, select_map)
        
        # Update mutual exclusive
        await self._update_mutual_exclusive(program, select_map)

    async def _update_option_availability(self, program: str, select_map: dict) -> None:
        """Update which options are available for the selected program."""
        
        # Steam available
        steam_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Perfect 20°C", "Деликатная"]
        steam_options = ["Без пара", "С паром"] if steam_available else ["Без пара"]
        if "input_select.bianca_steam" in select_map:
            await select_map["input_select.bianca_steam"].async_update_options(steam_options, "Без пара" if not steam_available else None)

        # Pre-wash available
        prewash_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани"]
        prewash_options = ["Нет", "Есть"] if prewash_available else ["Нет"]
        if "input_select.bianca_pre_wash" in select_map:
            await select_map["input_select.bianca_pre_wash"].async_update_options(prewash_options, "Нет" if not prewash_available else None)

        # Anti-crease and night spin availability
        anticrease_available = program not in ["Хлопок: Интенсивная стирка", "Хлопок", "Полоскание", "Слив + Отжим", "Perfect rapid 59 минут", "Быстрая"]
        nightspin_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Шерсть", "Деликатная", "Perfect 20°C"]
        
        mutual_exclusive = program in ["Синтетика и цветные ткани", "Шерсть", "Деликатная"]
        
        if mutual_exclusive:
            pass
        elif program in ["Хлопок: Интенсивная стирка", "Хлопок", "Perfect 20°C"]:
            if "input_select.bianca_anti_crease" in select_map:
                await select_map["input_select.bianca_anti_crease"].async_update_options(["Нет"], "Нет")
            if "input_select.bianca_night_spin" in select_map:
                night_options = ["Нет", "Есть"] if nightspin_available else ["Нет"]
                await select_map["input_select.bianca_night_spin"].async_update_options(night_options)
        elif anticrease_available and not nightspin_available:
            if "input_select.bianca_anti_crease" in select_map:
                anticrease_options = ["Нет", "Есть"] if anticrease_available else ["Нет"]
                await select_map["input_select.bianca_anti_crease"].async_update_options(anticrease_options)
            if "input_select.bianca_night_spin" in select_map:
                await select_map["input_select.bianca_night_spin"].async_update_options(["Нет"], "Нет")
        else:
            if "input_select.bianca_anti_crease" in select_map:
                anticrease_options = ["Нет", "Есть"] if anticrease_available else ["Нет"]
                await select_map["input_select.bianca_anti_crease"].async_update_options(anticrease_options)
            if "input_select.bianca_night_spin" in select_map:
                night_options = ["Нет", "Есть"] if nightspin_available else ["Нет"]
                await select_map["input_select.bianca_night_spin"].async_update_options(night_options)

        # Extra rinse available
        extra_rinse_available = program not in ["Perfect rapid 59 минут", "Быстрая", "Сохранить свежесть"]
        if not extra_rinse_available or program == "Полоскание":
            rinse_options = ["Нет"]
        elif program == "Шерсть":
            rinse_options = ["Нет", "1 полоскание"]
        else:
            rinse_options = ["Нет", "1 полоскание", "2 полоскания", "3 полоскания"]
        if "input_select.bianca_extra_rinse" in select_map:
            await select_map["input_select.bianca_extra_rinse"].async_update_options(rinse_options)

        # Aqua plus available
        aquaplus_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Perfect 20°C"]
        aquaplus_options = ["Нет", "Есть"] if aquaplus_available else ["Нет"]
        if "input_select.bianca_aqua_plus" in select_map:
            await select_map["input_select.bianca_aqua_plus"].async_update_options(aquaplus_options, "Нет" if not aquaplus_available else None)

        # Zoom available
        zoom_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Шерсть", "Perfect rapid 59 минут", "Деликатная"]
        zoom_options = ["Нет", "Есть"] if zoom_available else ["Нет"]
        if "input_select.bianca_zoom" in select_map:
            await select_map["input_select.bianca_zoom"].async_update_options(zoom_options, "Нет" if not zoom_available else None)

    async def _update_mutual_exclusive(self, program: str, select_map: dict) -> None:
        """Update mutual exclusive options (anti-crease vs night spin)."""
        pass


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
        _LOGGER.info(f"Temperature selected: {option}")
        await super().async_select_option(option)
        await self._update_hygiene_availability(option)

    async def _update_hygiene_availability(self, temperature: str) -> None:
        """Update hygiene option based on temperature."""
        selects = self._hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {}).get("selects", [])
        select_map = {s.entity_id: s for s in selects}
        
        program_select = select_map.get("input_select.bianca_program")
        if not program_select:
            return
        
        program = program_select.current_option
        hygiene_available = program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани"]
        temp_high = temperature in ["60°C", "90°C"]
        
        if hygiene_available and temp_high:
            hygiene_options = ["Нет", "Есть"]
            if "input_select.bianca_hygiene" in select_map:
                await select_map["input_select.bianca_hygiene"].async_update_options(hygiene_options)
        elif hygiene_available:
            if "input_select.bianca_hygiene" in select_map:
                await select_map["input_select.bianca_hygiene"].async_update_options(["Нет"], "Нет")


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
        _LOGGER.info(f"Anti-crease selected: {option}")
        await super().async_select_option(option)
        
        if option == "Есть":
            selects = self._hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {}).get("selects", [])
            select_map = {s.entity_id: s for s in selects}
            night_spin = select_map.get("input_select.bianca_night_spin")
            if night_spin and night_spin.current_option == "Есть":
                await night_spin.async_select_option("Нет")


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
        _LOGGER.info(f"Night spin selected: {option}")
        await super().async_select_option(option)
        
        if option == "Есть":
            selects = self._hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {}).get("selects", [])
            select_map = {s.entity_id: s for s in selects}
            anti_crease = select_map.get("input_select.bianca_anti_crease")
            if anti_crease and anti_crease.current_option == "Есть":
                await anti_crease.async_select_option("Нет")


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
