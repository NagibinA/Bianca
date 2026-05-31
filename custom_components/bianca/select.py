"""Select platform for Bianca integration."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers import entity_registry as er
from homeassistant.const import CONF_IP_ADDRESS

from .const import DOMAIN


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
    entities.append(BiancaTemperatureSelect(entry, hass, temp_options, default_temp))
    
    # Отжим
    spin_options, default_spin = get_spin_options(default_program)
    entities.append(BiancaSpinSelect(entry, hass, spin_options, default_spin))
    
    # Уровень загрязнения
    soil_options, default_soil = get_soil_options(default_program)
    entities.append(BiancaSoilSelect(entry, hass, soil_options, default_soil))
    
    # Пар
    steam_options, default_steam = get_steam_options(default_program)
    entities.append(BiancaSteamSelect(entry, hass, steam_options, default_steam))
    
    # Предварительная стирка
    prewash_options, default_prewash = get_prewash_options(default_program)
    entities.append(BiancaPreWashSelect(entry, hass, prewash_options, default_prewash))
    
    # Гигиена (зависит от программы и температуры)
    hygiene_options, default_hygiene = get_hygiene_options(default_program, default_temperature)
    entities.append(BiancaHygieneSelect(entry, hass, hygiene_options, default_hygiene))
    
    # Антисминание
    anticrease_options, default_anticrease = get_anticrease_options(default_program)
    entities.append(BiancaAntiCreaseSelect(entry, hass, anticrease_options, default_anticrease))
    
    # Ночная стирка
    nightspin_options, default_nightspin = get_nightspin_options(default_program)
    entities.append(BiancaNightSpinSelect(entry, hass, nightspin_options, default_nightspin))
    
    # Дополнительные полоскания
    rinses_options, default_rinse = get_rinses_options(default_program)
    entities.append(BiancaExtraRinseSelect(entry, hass, rinses_options, default_rinse))
    
    # Акваплюс
    aquaplus_options, default_aquaplus = get_aquaplus_options(default_program)
    entities.append(BiancaAquaPlusSelect(entry, hass, aquaplus_options, default_aquaplus))
    
    # Зум
    zoom_options, default_zoom = get_zoom_options(default_program)
    entities.append(BiancaZoomSelect(entry, hass, zoom_options, default_zoom))
    
    # Отложенный старт (всегда одинаковый)
    entities.append(BiancaDelayStartSelect(entry, hass))
    
    # Сохраняем ссылки на все созданные selects
    hass.data[DOMAIN][entry.entry_id]["selects"] = entities
    
    async_add_entities(entities)


# ========== ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ОПЦИЙ ==========

def get_temp_options(program: str) -> tuple[list[str], str]:
    """Get temperature options and default value for a program."""
    if program in ["Полоскание", "Слив + Отжим"]:
        return ["0°C"], "0°C"
    elif program == "Perfect 20°C":
        return ["0°C", "20°C"], "20°C"
    elif program in ["Шерсть", "Деликатная", "Сохранить свежесть"]:
        return ["0°C", "20°C", "30°C", "40°C"], "30°C" if program in ["Шерсть", "Деликатная"] else "20°C"
    elif program in ["Быстрая", "Perfect rapid 59 минут"]:
        return ["0°C", "20°C", "30°C", "40°C", "60°C"], "40°C"
    elif program in ["Хлопок", "Синтетика и цветные ткани"]:
        return ["0°C", "20°C", "30°C", "40°C", "60°C"], "40°C"
    elif program in ["Хлопок: Интенсивная стирка"]:
        return ["0°C", "20°C", "30°C", "40°C", "60°C", "90°C"], "60°C"
    else:
        return ["0°C", "20°C", "30°C", "40°C"], "30°C"


def get_spin_options(program: str) -> tuple[list[str], str]:
    """Get spin options and default value for a program."""
    if program in ["Шерсть"]:
        return ["0 об/мин", "400 об/мин", "500 об/мин", "600 об/мин", "700 об/мин", "800 об/мин"], "800 об/мин"
    elif program == "Сохранить свежесть":
        return ["0 об/мин", "400 об/мин", "600 об/мин", "800 об/мин"], "800 об/мин"
    elif program == "Деликатная":
        return ["0 об/мин", "400 об/мин"], "400 об/мин"
    elif program in ["Perfect rapid 59 минут", "Полоскание"]:
        return ["0 об/мин", "400 об/мин", "500 об/мин", "600 об/мин", "700 об/мин", "800 об/мин", "900 об/мин", "1000 об/мин"], "1000 об/мин"
    else:
        return ["0 об/мин", "400 об/мин", "600 об/мин", "700 об/мин", "800 об/мин", "900 об/мин", "1000 об/мин", "1100 об/мин", "1200 об/мин", "1300 об/мин", "1400 об/мин"], "1000 об/мин"


def get_soil_options(program: str) -> tuple[list[str], str]:
    """Get soil level options and default value for a program."""
    if program in ["Perfect 20°C"]:
        return ["Нормально"], "Нормально"
    elif program in ["Шерсть", "Деликатная", "Полоскание", "Слив + Отжим", "Сохранить свежесть", "Perfect rapid 59 минут"]:
        return ["Нет"], "Нет"
    else:
        return ["Нет", "Мало", "Нормально", "Очень"], "Нет"


def get_steam_options(program: str) -> tuple[list[str], str]:
    """Get steam options and default value for a program."""
    if program in ["Хлопок: Интенсивная стирка", "Хлопок", "Синтетика и цветные ткани", "Perfect 20°C", "Деликатная"]:
        return ["Без пара", "С паром"], "Без пара"
    return ["Без пара"], "Без пара"


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


# ========== ФУНКЦИИ ДЛЯ ПЕРЕСОЗДАНИЯ СЕЛЕКТОВ ==========

async def recreate_select(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
    select_type: str,
    create_func,
    *args,
) -> None:
    """Delete old select and create a new one."""
    entity_registry = er.async_get(hass)
    
    # Находим старую сущность
    old_entity_id = None
    for entity in list(entity_registry.entities.values()):
        if entity.config_entry_id == entry.entry_id and entity.unique_id.endswith(select_type):
            old_entity_id = entity.entity_id
            break
    
    if not old_entity_id:
        old_entity_id = f"select.bianca_{select_type}"
    
    # Удаляем старую сущность
    if old_entity_id in [e.entity_id for e in list(entity_registry.entities.values())]:
        entity_registry.async_remove(old_entity_id)
    
    # Создаём новую сущность с тем же entity_id
    new_entity = create_func(*args, old_entity_id)
    
    # Добавляем через сохранённый коллбэк
    add_callback = hass.data[DOMAIN][entry.entry_id]["async_add_entities"]
    if add_callback:
        add_callback([new_entity])
    
    return new_entity


async def recreate_all_selects(hass: HomeAssistant, entry: ConfigEntry, program: str) -> None:
    """Recreate all dependent selects when program changes."""
    
    # Получаем текущую температуру для гигиены
    temp_select = hass.states.get("select.bianca_temperature")
    current_temperature = temp_select.state if temp_select else "60°C"
    
    # Температура
    temp_options, default_temp = get_temp_options(program)
    await recreate_select(
        hass, entry, "temperature",
        lambda eid: BiancaTemperatureSelect(entry, hass, temp_options, default_temp, eid)
    )
    
    # Отжим
    spin_options, default_spin = get_spin_options(program)
    await recreate_select(
        hass, entry, "spin",
        lambda eid: BiancaSpinSelect(entry, hass, spin_options, default_spin, eid)
    )
    
    # Уровень загрязнения
    soil_options, default_soil = get_soil_options(program)
    await recreate_select(
        hass, entry, "soil",
        lambda eid: BiancaSoilSelect(entry, hass, soil_options, default_soil, eid)
    )
    
    # Пар
    steam_options, default_steam = get_steam_options(program)
    await recreate_select(
        hass, entry, "steam",
        lambda eid: BiancaSteamSelect(entry, hass, steam_options, default_steam, eid)
    )
    
    # Предварительная стирка
    prewash_options, default_prewash = get_prewash_options(program)
    await recreate_select(
        hass, entry, "pre_wash",
        lambda eid: BiancaPreWashSelect(entry, hass, prewash_options, default_prewash, eid)
    )
    
    # Гигиена
    hygiene_options, default_hygiene = get_hygiene_options(program, current_temperature)
    await recreate_select(
        hass, entry, "hygiene",
        lambda eid: BiancaHygieneSelect(entry, hass, hygiene_options, default_hygiene, eid)
    )
    
    # Антисминание
    anticrease_options, default_anticrease = get_anticrease_options(program)
    await recreate_select(
        hass, entry, "anti_crease",
        lambda eid: BiancaAntiCreaseSelect(entry, hass, anticrease_options, default_anticrease, eid)
    )
    
    # Ночная стирка
    nightspin_options, default_nightspin = get_nightspin_options(program)
    await recreate_select(
        hass, entry, "night_spin",
        lambda eid: BiancaNightSpinSelect(entry, hass, nightspin_options, default_nightspin, eid)
    )
    
    # Дополнительные полоскания
    rinses_options, default_rinse = get_rinses_options(program)
    await recreate_select(
        hass, entry, "extra_rinse",
        lambda eid: BiancaExtraRinseSelect(entry, hass, rinses_options, default_rinse, eid)
    )
    
    # Акваплюс
    aquaplus_options, default_aquaplus = get_aquaplus_options(program)
    await recreate_select(
        hass, entry, "aqua_plus",
        lambda eid: BiancaAquaPlusSelect(entry, hass, aquaplus_options, default_aquaplus, eid)
    )
    
    # Зум
    zoom_options, default_zoom = get_zoom_options(program)
    await recreate_select(
        hass, entry, "zoom",
        lambda eid: BiancaZoomSelect(entry, hass, zoom_options, default_zoom, eid)
    )


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
        fixed_entity_id: str = None,
    ) -> None:
        """Initialize the select."""
        self._entry = entry
        self._hass = hass
        if fixed_entity_id:
            self.entity_id = fixed_entity_id
        else:
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
    
    async def async_update_options(self, options: list[str], current_option: str = None) -> None:
        """Update available options dynamically."""
        self._attr_options = options
        if current_option and current_option in options:
            self._attr_current_option = current_option
        elif self._attr_current_option not in options:
            self._attr_current_option = options[0]
        self.async_write_ha_state()


# ========== ПРОГРАММА ==========

class BiancaProgramSelect(BiancaBaseSelect):
    """Program selection that triggers recreation of all dependent selects."""

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
        """Update current option and recreate all dependent selects."""
        self._attr_current_option = option
        self.async_write_ha_state()
        await recreate_all_selects(self._hass, self._entry, option)


# ========== ЗАВИСИМЫЕ СЕЛЕКТЫ ==========

class BiancaTemperatureSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "temperature", "Температура стирки", "mdi:thermometer",
            options, default_option, fixed_entity_id
        )

    async def async_select_option(self, option: str) -> None:
        """Update temperature and handle hygiene availability."""
        await super().async_select_option(option)
        
        program_select = self._hass.states.get("select.bianca_program")
        if not program_select:
            return
        
        program = program_select.state
        
        # Пересоздаём гигиену с учётом новой температуры
        hygiene_options, default_hygiene = get_hygiene_options(program, option)
        
        entity_registry = er.async_get(self._hass)
        
        old_entity_id = None
        for entity in list(entity_registry.entities.values()):
            if entity.config_entry_id == self._entry.entry_id and entity.unique_id.endswith("hygiene"):
                old_entity_id = entity.entity_id
                break
        
        if old_entity_id:
            entity_registry.async_remove(old_entity_id)
        
        new_entity = BiancaHygieneSelect(self._entry, self._hass, hygiene_options, default_hygiene, old_entity_id)
        
        add_callback = self._hass.data[DOMAIN][self._entry.entry_id]["async_add_entities"]
        if add_callback:
            add_callback([new_entity])


class BiancaSpinSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "spin", "Скорость отжима", "mdi:rotate-right",
            options, default_option, fixed_entity_id
        )


class BiancaDelayStartSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, fixed_entity_id=None):
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
            options, "Нет", fixed_entity_id
        )


class BiancaSoilSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "soil", "Уровень загрязнения", "mdi:water-percent",
            options, default_option, fixed_entity_id
        )


class BiancaSteamSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "steam", "Пар", "mdi:water-vapor",
            options, default_option, fixed_entity_id
        )


class BiancaPreWashSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "pre_wash", "Предварительная стирка", "mdi:soap",
            options, default_option, fixed_entity_id
        )


class BiancaHygieneSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "hygiene", "Гигиеническая стирка", "mdi:sterling",
            options, default_option, fixed_entity_id
        )


class BiancaAntiCreaseSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "anti_crease", "Анти сминание", "mdi:iron",
            options, default_option, fixed_entity_id
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
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "night_spin", "Ночной отжим", "mdi:weather-night",
            options, default_option, fixed_entity_id
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
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "extra_rinse", "Дополнительные полоскания", "mdi:water",
            options, default_option, fixed_entity_id
        )


class BiancaAquaPlusSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "aqua_plus", "Акваплюс", "mdi:water-plus",
            options, default_option, fixed_entity_id
        )


class BiancaZoomSelect(BiancaBaseSelect):
    def __init__(self, entry, hass, options, default_option=None, fixed_entity_id=None):
        super().__init__(
            entry, hass, "zoom", "Режим ZOOM", "mdi:arrow-expand-all",
            options, default_option, fixed_entity_id
        )
