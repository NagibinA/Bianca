"""
Select platform for Bianca integration.
Version: 1.0.34

ИЗМЕНЕНИЯ В ЭТОЙ ВЕРСИИ (1.0.34):
- Исправлен сброс всех селектов при выборе температуры
- При изменении температуры обновляется только гигиена (зависит от температуры)
- Остальные селекты сохраняют выбранные пользователем значения
"""

from __future__ import annotations

import logging
from homeassistant.components.select import SelectEntity
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
    """Set up Bianca selects dynamically."""
    
    # Сохраняем коллбэк для динамического добавления
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id]["async_add_entities"] = async_add_entities
    
    # Создаём программу (всегда есть)
    entities = [
        BiancaProgramSelect(entry, hass),
    ]
    
    # Создаём все зависимые селекты с опциями по умолчанию
    default_program = "Хлопок: Интенсивная стирка"
    default_temperature = "60°C"
    
    # Температура
    temp_options, default_temp = get_temp_options(default_program)
    temp_select = BiancaTemperatureSelect(entry, hass, temp_options, default_temp)
    entities.append(temp_select)
    
    # Отжим
    spin_options, default_spin = get_spin_options(default_program)
    spin_select = BiancaSpinSelect(entry, hass, spin_options, default_spin)
    entities.append(spin_select)
    
    # Уровень загрязнения
    soil_options, default_soil = get_soil_options(default_program)
    soil_select = BiancaSoilSelect(entry, hass, soil_options, default_soil)
    entities.append(soil_select)
    
    # Пар
    steam_options, default_steam = get_steam_options(default_program)
    steam_select = BiancaSteamSelect(entry, hass, steam_options, default_steam)
    entities.append(steam_select)
    
    # Предварительная стирка
    prewash_options, default_prewash = get_prewash_options(default_program)
    prewash_select = BiancaPreWashSelect(entry, hass, prewash_options, default_prewash)
    entities.append(prewash_select)
    
    # Гигиена (зависит от программы и температуры)
    hygiene_options, default_hygiene = get_hygiene_options(default_program, default_temperature)
    hygiene_select = BiancaHygieneSelect(entry, hass, hygiene_options, default_hygiene)
    entities.append(hygiene_select)
    
    # Антисминание
    anticrease_options, default_anticrease = get_anticrease_options(default_program)
    anticrease_select = BiancaAntiCreaseSelect(entry, hass, anticrease_options, default_anticrease)
    entities.append(anticrease_select)
    
    # Ночная стирка
    nightspin_options, default_nightspin = get_nightspin_options(default_program)
    nightspin_select = BiancaNightSpinSelect(entry, hass, nightspin_options, default_nightspin)
    entities.append(nightspin_select)
    
    # Дополнительные полоскания
    rinses_options, default_rinse = get_rinses_options(default_program)
    rinses_select = BiancaExtraRinseSelect(entry, hass, rinses_options, default_rinse)
    entities.append(rinses_select)
    
    # Акваплюс
    aquaplus_options, default_aquaplus = get_aquaplus_options(default_program)
    aquaplus_select = BiancaAquaPlusSelect(entry, hass, aquaplus_options, default_aquaplus)
    entities.append(aquaplus_select)
    
    # Зум
    zoom_options, default_zoom = get_zoom_options(default_program)
    zoom_select = BiancaZoomSelect(entry, hass, zoom_options, default_zoom)
    entities.append(zoom_select)
    
    # Отложенный старт (всегда одинаковый)
    delay_select = BiancaDelayStartSelect(entry, hass)
    entities.append(delay_select)
    
    # Сохраняем ссылки на все созданные selects для прямого доступа
    hass.data[DOMAIN][entry.entry_id]["selects"] = {
        "temperature": temp_select,
        "spin": spin_select,
        "soil": soil_select,
        "steam": steam_select,
        "pre_wash": prewash_select,
        "hygiene": hygiene_select,
        "anti_crease": anticrease_select,
        "night_spin": nightspin_select,
        "extra_rinse": rinses_select,
        "aqua_plus": aquaplus_select,
        "zoom": zoom_select,
        "delay_start": delay_select,
    }
    
    async_add_entities(entities)


# ========== ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ОПЦИЙ (по scripts.yaml) ==========

def get_temp_options(program: str) -> tuple[list[str], str]:
    """Get temperature options and default value for a program."""
    if program in ["Полоскание", "Слив + Отжим"]:
        return ["0°C"], "0°C"
    elif program == "Perfect 20°C":
        return ["0°C", "20°C"], "20°C"
    elif program in ["Шерсть", "Деликатная", "Сохранить свежесть"]:
        return ["0°C", "20°C", "30°C", "40°C"], "30°C" if program in ["Шерсть", "Деликатная"] else "20°C"
    elif program in ["Быстрая", "Perfect rapid 59 минут", "Хлопок", "Синтетика и цветные ткани"]:
        return ["0°C", "20°C", "30°C", "40°C", "60°C"], "40°C"
    elif program in ["Хлопок: Интенсивная стирка"]:
        return ["0°C", "20°C", "30°C", "40°C", "60°C", "90°C"], "60°C"
    else:
        return ["0°C", "20°C", "30°C", "40°C"], "30°C"


def get_spin_options(program: str) -> tuple[list[str], str]:
    """Get spin options and default value for a program."""
    if program == "Шерсть":
        return ["0 об/мин", "400 об/мин", "500 об/мин", "600 об/мин", "700 об/мин", "800 об/мин"], "800 об/мин"
    elif program == "Сохранить свежесть":
        return ["0 об/мин", "400 об/мин", "600 об/мин", "800 об/мин"], "800 об/мин"
    elif program == "Деликатная":
        return ["0 об/мин", "400 об/мин"], "400 об/мин"
    elif program in ["Perfect rapid 59 минут", "Полоскание"]:
        return ["0 об/мин", "400 об/мин", "500 об/мин", "600 об/мин", "700 об/мин", "800 об/мин", "900 об/мин", "1000 об/мин"], "1000 об/мин"
    elif program in ["Хлопок: Интенсивная стирка", "Слив + Отжим", "Хлопок"]:
        return ["0 об/мин", "400 об/мин", "600 об/мин", "700 об/мин", "800 об/мин", "900 об/мин", "1000 об/мин", "1100 об/мин", "1200 об/мин", "1300 об/мин", "1400 об/мин"], "1000 об/мин"
    else:
        return ["0 об/мин", "400 об/мин", "600 об/мин", "700 об/мин", "800 об/мин", "900 об/мин", "1000 об/мин", "1100 об/мин", "1200 об/мин", "1300 об/мин", "1400 об/мин"], "1000 об/мин"


def get_soil_options(program: str) -> tuple[list[str], str]:
    """Get soil level options and default value for a program."""
    if program == "Perfect 20°C":
        return ["Нормально"], "Нормально"
    elif program in ["Шерсть", "Деликатная", "Полоскание", "Слив + Отжим", "Сохранить свежесть", "Perfect rapid 59 минут"]:
        return ["Нет"], "Нет"
    else:
        return ["Мало", "Нормально", "Очень"], "Мало"


def get_steam_options(program: str) -> tuple[list[str], str]:
    """Get steam options and default value for a program."""
    if program in ["Шерсть", "Полоскание", "Слив + Отжим"]:
        return ["Без пара"], "Без пара"
    else:
        return ["Без пара", "С паром"], "Без пара"


def get_prewash_options(program: str) -> tuple[list[str], str]:
    """Get pre-wash options and default value for a program."""
    if program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани"]:
        return ["Нет", "Есть"], "Нет"
    return ["Нет"], "Нет"


def get_hygiene_options(program: str, temperature: str = "0°C") -> tuple[list[str], str]:
    """Get hygiene options based on program AND temperature."""
    if program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани"]:
        if temperature in ["60°C", "90°C"]:
            return ["Нет", "Есть"], "Нет"
    return ["Нет"], "Нет"


def get_anticrease_options(program: str) -> tuple[list[str], str]:
    """Get anti-crease options for a program."""
    if program in ["Хлопок: Интенсивная стирка", "Хлопок", "Полоскание", "Слив + Отжим", "Perfect rapid 59 минут", "Быстрая"]:
        return ["Нет"], "Нет"
    return ["Нет", "Есть"], "Нет"


def get_nightspin_options(program: str) -> tuple[list[str], str]:
    """Get night spin options for a program."""
    if program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Шерсть", "Деликатная", "Perfect 20°C"]:
        return ["Нет", "Есть"], "Нет"
    return ["Нет"], "Нет"


def get_rinses_options(program: str) -> tuple[list[str], str]:
    """Get extra rinse options for a program."""
    if program in ["Perfect rapid 59 минут", "Быстрая", "Сохранить свежесть"]:
        return ["Нет"], "Нет"
    elif program == "Шерсть":
        return ["Нет", "1 полоскание"], "Нет"
    elif program == "Полоскание":
        return ["Нет"], "Нет"
    else:
        return ["Нет", "1 полоскание", "2 полоскания", "3 полоскания"], "Нет"


def get_aquaplus_options(program: str) -> tuple[list[str], str]:
    """Get aqua plus options for a program."""
    if program in ["Хлопок: Интенсивная стирка", "Хлопок", "Perfect 20°C"]:
        return ["Нет", "Есть"], "Нет"
    return ["Нет"], "Нет"


def get_zoom_options(program: str) -> tuple[list[str], str]:
    """Get zoom options for a program."""
    if program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Шерсть", "Perfect rapid 59 минут", "Деликатная"]:
        return ["Нет", "Есть"], "Нет"
    return ["Нет"], "Нет"


# ========== ФУНКЦИЯ ОБНОВЛЕНИЯ ВСЕХ СЕЛЕКТОВ ПРИ СМЕНЕ ПРОГРАММЫ ==========

async def update_all_selects(hass: HomeAssistant, entry: ConfigEntry, program: str) -> None:
    """
    Обновляет опции всех селектов при смене программы.
    Использует прямые ссылки на объекты селектов.
    """
    selects = hass.data[DOMAIN][entry.entry_id].get("selects", {})
    
    if not selects:
        _LOGGER.warning("No selects found in storage")
        return
    
    # Получаем текущую температуру
    temp_select = hass.states.get("select.bianca_temperature")
    temperature = temp_select.state if temp_select else "60°C"
    
    # Обновляем температуру
    temp_options, default_temp = get_temp_options(program)
    if "temperature" in selects:
        selects["temperature"].update_options(temp_options, default_temp)
    
    # Обновляем отжим
    spin_options, default_spin = get_spin_options(program)
    if "spin" in selects:
        selects["spin"].update_options(spin_options, default_spin)
    
    # Обновляем уровень загрязнения
    soil_options, default_soil = get_soil_options(program)
    if "soil" in selects:
        selects["soil"].update_options(soil_options, default_soil)
    
    # Обновляем пар
    steam_options, default_steam = get_steam_options(program)
    if "steam" in selects:
        selects["steam"].update_options(steam_options, default_steam)
    
    # Обновляем предварительную стирку
    prewash_options, default_prewash = get_prewash_options(program)
    if "pre_wash" in selects:
        selects["pre_wash"].update_options(prewash_options, default_prewash)
    
    # Обновляем гигиену
    hygiene_options, default_hygiene = get_hygiene_options(program, temperature)
    if "hygiene" in selects:
        selects["hygiene"].update_options(hygiene_options, default_hygiene)
    
    # Обновляем антисминание
    anticrease_options, default_anticrease = get_anticrease_options(program)
    if "anti_crease" in selects:
        selects["anti_crease"].update_options(anticrease_options, default_anticrease)
    
    # Обновляем ночную стирку
    nightspin_options, default_nightspin = get_nightspin_options(program)
    if "night_spin" in selects:
        selects["night_spin"].update_options(nightspin_options, default_nightspin)
    
    # Обновляем дополнительные полоскания
    rinses_options, default_rinse = get_rinses_options(program)
    if "extra_rinse" in selects:
        selects["extra_rinse"].update_options(rinses_options, default_rinse)
    
    # Обновляем акваплюс
    aquaplus_options, default_aquaplus = get_aquaplus_options(program)
    if "aqua_plus" in selects:
        selects["aqua_plus"].update_options(aquaplus_options, default_aquaplus)
    
    # Обновляем зум
    zoom_options, default_zoom = get_zoom_options(program)
    if "zoom" in selects:
        selects["zoom"].update_options(zoom_options, default_zoom)


# ========== ФУНКЦИЯ ОБНОВЛЕНИЯ ТОЛЬКО ГИГИЕНЫ ПРИ СМЕНЕ ТЕМПЕРАТУРЫ ==========

async def update_hygiene_only(hass: HomeAssistant, entry: ConfigEntry, program: str, temperature: str) -> None:
    """
    Обновляет только опции гигиены при смене температуры.
    Остальные селекты не трогаем.
    """
    selects = hass.data[DOMAIN][entry.entry_id].get("selects", {})
    
    if not selects:
        _LOGGER.warning("No selects found in storage")
        return
    
    # Обновляем только гигиену
    hygiene_options, default_hygiene = get_hygiene_options(program, temperature)
    if "hygiene" in selects:
        selects["hygiene"].update_options(hygiene_options, default_hygiene)


# ========== БАЗОВЫЙ КЛАСС ==========

class BiancaBaseSelect(SelectEntity):
    """Base class for Bianca selects."""

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
        self.entity_id = f"select.bianca_{entity_id_key}"
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
    
    def update_options(self, options: list[str], current_option: str = None) -> None:
        """
        Update available options dynamically.
        Вызывается синхронно из update_all_selects и update_hygiene_only.
        """
        self._attr_options = options
        if current_option and current_option in options:
            self._attr_current_option = current_option
        elif self._attr_current_option not in options:
            self._attr_current_option = options[0]
        self.async_write_ha_state()


# ========== ПРОГРАММА ==========

class BiancaProgramSelect(BiancaBaseSelect):
    """Program selection that triggers update of all dependent selects."""

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
        """Update current option and update all dependent selects."""
        self._attr_current_option = option
        self.async_write_ha_state()
        await update_all_selects(self._hass, self._entry, option)


# ========== ЗАВИСИМЫЕ СЕЛЕКТЫ ==========

class BiancaTemperatureSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "temperature", "Температура стирки", "mdi:thermometer",
            options, default_option
        )

    async def async_select_option(self, option: str) -> None:
        """Update temperature and update only hygiene (depends on temperature)."""
        await super().async_select_option(option)
        
        program_select = self._hass.states.get("select.bianca_program")
        if program_select:
            # Обновляем только гигиену, остальные селекты не трогаем
            await update_hygiene_only(self._hass, self._entry, program_select.state, option)


class BiancaSpinSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "spin", "Скорость отжима", "mdi:rotate-right",
            options, default_option
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
            entry, hass, "delay_start", "Отложенный старт", "mdi:timer-outline",
            options, "Нет"
        )


class BiancaSoilSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "soil", "Уровень загрязнения", "mdi:water-percent",
            options, default_option
        )


class BiancaSteamSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "steam", "Пар", "mdi:water-vapor",
            options, default_option
        )


class BiancaPreWashSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "pre_wash", "Предварительная стирка", "mdi:soap",
            options, default_option
        )


class BiancaHygieneSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "hygiene", "Гигиеническая стирка", "mdi:sterling",
            options, default_option
        )


class BiancaAntiCreaseSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "anti_crease", "Анти сминание", "mdi:iron",
            options, default_option
        )

    async def async_select_option(self, option: str) -> None:
        await super().async_select_option(option)
        
        program_select = self._hass.states.get("select.bianca_program")
        if not program_select:
            return
        
        program = program_select.state
        mutual_exclusive = program in ["Синтетика и цветные ткани", "Шерсть", "Деликатная"]
        
        if mutual_exclusive and option == "Есть":
            night_spin = self._hass.states.get("select.bianca_night_spin")
            if night_spin and night_spin.state == "Есть":
                await self._hass.services.async_call(
                    "select", "select_option",
                    {"entity_id": "select.bianca_night_spin", "option": "Нет"}
                )


class BiancaNightSpinSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "night_spin", "Ночной отжим", "mdi:weather-night",
            options, default_option
        )

    async def async_select_option(self, option: str) -> None:
        await super().async_select_option(option)
        
        program_select = self._hass.states.get("select.bianca_program")
        if not program_select:
            return
        
        program = program_select.state
        mutual_exclusive = program in ["Синтетика и цветные ткани", "Шерсть", "Деликатная"]
        
        if mutual_exclusive and option == "Есть":
            anti_crease = self._hass.states.get("select.bianca_anti_crease")
            if anti_crease and anti_crease.state == "Есть":
                await self._hass.services.async_call(
                    "select", "select_option",
                    {"entity_id": "select.bianca_anti_crease", "option": "Нет"}
                )


class BiancaExtraRinseSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "extra_rinse", "Дополнительные полоскания", "mdi:water",
            options, default_option
        )


class BiancaAquaPlusSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "aqua_plus", "Акваплюс", "mdi:water-plus",
            options, default_option
        )


class BiancaZoomSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None):
        super().__init__(
            entry, hass, "zoom", "Режим ZOOM", "mdi:arrow-expand-all",
            options, default_option
        )
