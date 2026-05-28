"""Sensor platform for Bianca integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfTime,
    UnitOfFrequency,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import BiancaDataUpdateCoordinator

# Mapping tables
MACHMD_MAP = {
    "1": "Бездействие",
    "2": "Работает",
    "3": "Пауза",
    "4": "Выбор отложенного запуска",
    "5": "Задан отложенный запуск",
    "6": "Ошибка",
    "7": "Завершено",
    "8": "Завершено",
}

PR_MAP = {
    "0": "Выключено",
    "1": "Хлопок: Интенсивная стирка",
    "2": "Хлопок",
    "3": "Синтетика и цветные ткани",
    "4": "Шерсть",
    "5": "Деликатная",
    "6": "Perfect 20°C",
    "7": "Полоскание",
    "8": "Слив + Отжим",
    "13": "Сохранить свежесть",
    "15": "Perfect rapid 59 минут",
    "16": "Быстрая",
}

PRPH_MAP = {
    "0": "Остановлено",
    "1": "Предварительная стирка",
    "2": "Стирка",
    "3": "Полоскание",
    "4": "Последнее полоскание",
    "5": "Конец",
    "7": "Ошибка",
    "8": "Пар",
    "9": "Ночной отжим",
    "10": "Отжим",
}

ERR_MAP = {
    "0": "Нет ошибок",
    "2": "Машина не может набрать воду",
    "3": "Стиральная машина не сливает воду",
    "4": "Слишком много пены и/или воды",
    "7": "Проблема с дверцей",
}

LANG_MAP = {
    "7": "Русский",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca sensors."""
    coordinator: BiancaDataUpdateCoordinator = entry.runtime_data
    
    entities = [
        BiancaWiFiStatusSensor(coordinator, entry),
        BiancaErrorSensor(coordinator, entry),
        BiancaMachineModeSensor(coordinator, entry),
        BiancaProgramSensor(coordinator, entry),
        BiancaProgramPhaseSensor(coordinator, entry),
        BiancaSoilLevelSensor(coordinator, entry),
        BiancaTemperatureSensor(coordinator, entry),
        BiancaSpinSpeedSensor(coordinator, entry),
        BiancaRemainingTimeSensor(coordinator, entry),
        BiancaDelayStartSensor(coordinator, entry),
        BiancaLanguageSensor(coordinator, entry),
        BiancaSteamSensor(coordinator, entry),
        BiancaPreWashSensor(coordinator, entry),
        BiancaHygienicSensor(coordinator, entry),
        BiancaAntiCreaseSensor(coordinator, entry),
        BiancaNightSpinSensor(coordinator, entry),
        BiancaRinse1Sensor(coordinator, entry),
        BiancaRinse2Sensor(coordinator, entry),
        BiancaRinse3Sensor(coordinator, entry),
        BiancaAquaPlusSensor(coordinator, entry),
        BiancaZoomSensor(coordinator, entry),
    ]
    
    async_add_entities(entities)


class BiancaBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Bianca sensors."""

    def __init__(
        self, 
        coordinator: BiancaDataUpdateCoordinator, 
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        unit: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"{entry.title} {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)


class BiancaWiFiStatusSensor(BiancaBaseSensor):
    """WiFi status sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "WiFiStatus", "WiFi статус", "mdi:wifi")

    @property
    def native_value(self):
        value = super().native_value
        if value == "1":
            return "Управление разрешено"
        elif value == "0":
            return "Управление запрещено"
        return value


class BiancaErrorSensor(BiancaBaseSensor):
    """Error sensor with text description."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Err", "Ошибка", "mdi:alert-circle")

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        if value == "0":
            return "Нет ошибок"
        return ERR_MAP.get(value, f"Неизвестная ошибка ({value})")


class BiancaMachineModeSensor(BiancaBaseSensor):
    """Machine mode sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "MachMd", "Состояние машины", "mdi:washing-machine")

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return MACHMD_MAP.get(value, value)


class BiancaProgramSensor(BiancaBaseSensor):
    """Program sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Pr", "Программа стирки", "mdi:format-list-bulleted")

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return PR_MAP.get(value, value)


class BiancaProgramPhaseSensor(BiancaBaseSensor):
    """Program phase sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "PrPh", "Фаза программы", "mdi:progress-clock")

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return PRPH_MAP.get(value, value)


class BiancaSoilLevelSensor(BiancaBaseSensor):
    """Soil level sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(
            coordinator, entry, "SLevel", "Уровень загрязнения", "mdi:water-percent",
            state_class=SensorStateClass.MEASUREMENT
        )

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        levels = {"1": "Низкий", "2": "Средний", "3": "Высокий"}
        return levels.get(value, value)


class BiancaTemperatureSensor(BiancaBaseSensor):
    """Temperature sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(
            coordinator, entry, "Temp", "Температура стирки", "mdi:thermometer",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            unit=UnitOfTemperature.CELSIUS
        )


class BiancaSpinSpeedSensor(BiancaBaseSensor):
    """Spin speed sensor (value × 100 = RPM)."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(
            coordinator, entry, "SpinSp", "Скорость отжима", "mdi:sync",
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT,
            unit=UnitOfFrequency.REVOLUTIONS_PER_MINUTE
        )

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        try:
            return int(value) * 100
        except (ValueError, TypeError):
            return value


class BiancaRemainingTimeSensor(BiancaBaseSensor):
    """Remaining time sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(
            coordinator, entry, "RemTime", "Оставшееся время", "mdi:timer-outline",
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            unit=UnitOfTime.SECONDS
        )


class BiancaDelayStartSensor(BiancaBaseSensor):
    """Delay start sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(
            coordinator, entry, "DelVal", "Отложенный старт", "mdi:calendar-clock",
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            unit=UnitOfTime.SECONDS
        )


class BiancaLanguageSensor(BiancaBaseSensor):
    """Language sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Lang", "Язык дисплея", "mdi:translate")

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return LANG_MAP.get(value, value)


class BiancaSteamSensor(BiancaBaseSensor):
    """Steam sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Steam", "Пар", "mdi:water-vapor")

    @property
    def native_value(self):
        value = super().native_value
        if value == "1":
            return "Включен"
        elif value == "0":
            return "Выключен"
        return value


class BiancaPreWashSensor(BiancaBaseSensor):
    """Pre-wash option sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Opt1", "Предварительная стирка", "mdi:tshirt-crew")

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaHygienicSensor(BiancaBaseSensor):
    """Hygienic wash option sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Opt2", "Гигиеническая стирка", "mdi:disinfectant")

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaAntiCreaseSensor(BiancaBaseSensor):
    """Anti-crease option sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Opt3", "Анти сминание", "mdi:iron")

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaNightSpinSensor(BiancaBaseSensor):
    """Night spin option sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Opt4", "Ночной отжим", "mdi:weather-night")

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaRinse1Sensor(BiancaBaseSensor):
    """Rinse 1 option sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Opt5", "Полоскание 1", "mdi:water")

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaRinse2Sensor(BiancaBaseSensor):
    """Rinse 2 option sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Opt6", "Полоскание 2", "mdi:water")

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaRinse3Sensor(BiancaBaseSensor):
    """Rinse 3 option sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Opt7", "Полоскание 3", "mdi:water")

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaAquaPlusSensor(BiancaBaseSensor):
    """Aqua plus option sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Opt8", "Акваплюс", "mdi:water-plus")

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaZoomSensor(BiancaBaseSensor):
    """ZOOM mode sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry, "Opt9", "Режим ZOOM", "mdi:magnify")

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"
