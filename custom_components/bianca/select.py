"""Select platform for Bianca integration."""
from __future__ import annotations

import logging
from homeassistant.components.select import SelectEntity
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
    """Program selection."""

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


class BiancaTemperatureSelect(BiancaBaseSelect):
    """Temperature selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "temperature", "Температура стирки", "mdi:thermometer",
            ["0°C", "20°C", "30°C", "40°C", "60°C", "90°C"]
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
    """Anti-crease selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "anti_crease", "Анти сминание", "mdi:iron",
            ["Нет", "Есть"]
        )


class BiancaNightSpinSelect(BiancaBaseSelect):
    """Night spin selection."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass,
            "night_spin", "Ночной отжим", "mdi:weather-night",
            ["Нет", "Есть"]
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
