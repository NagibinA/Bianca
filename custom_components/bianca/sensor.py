"""Sensor platform for Bianca integration."""

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
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from . import BiancaConfigEntry
from .const import (
    DOMAIN,
    KEY_WIFISTATUS,
    KEY_ERR,
    KEY_MACHMD,
    KEY_PR,
    KEY_PRPH,
    KEY_SLEVEL,
    KEY_TEMP,
    KEY_SPINSP,
    KEY_REMTIME,
    KEY_DELVAL,
    KEY_LANG,
    MACHMD_MAP,
    PR_MAP,
    PRPH_MAP,
    ERR_MAP,
    LANG_MAP,
)
from .coordinator import BiancaDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BiancaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca sensors based on a config entry."""
    coordinator = entry.runtime_data.coordinator
    
    sensors = [
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
    ]
    
    async_add_entities(sensors, True)


class BiancaBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Bianca sensors."""

    def __init__(
        self,
        coordinator: BiancaDataUpdateCoordinator,
        entry,
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
        self._attr_should_poll = False

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)


class BiancaWiFiStatusSensor(BiancaBaseSensor):
    """WiFi status sensor (1=remote control allowed, 0=disabled)."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_WIFISTATUS, "WiFi статус", "mdi:wifi"
        )

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

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_ERR, "Ошибка", "mdi:alert-circle"
        )

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return ERR_MAP.get(value, f"Неизвестная ошибка ({value})" if value != "0" else value)


class BiancaMachineModeSensor(BiancaBaseSensor):
    """Machine mode sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_MACHMD, "Состояние машины", "mdi:washing-machine"
        )

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return MACHMD_MAP.get(value, value)


class BiancaProgramSensor(BiancaBaseSensor):
    """Program sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_PR, "Программа стирки", "mdi:format-list-bulleted"
        )

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return PR_MAP.get(value, value)


class BiancaProgramPhaseSensor(BiancaBaseSensor):
    """Program phase sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_PRPH, "Фаза программы", "mdi:progress-clock"
        )

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return PRPH_MAP.get(value, value)


class BiancaSoilLevelSensor(BiancaBaseSensor):
    """Soil level sensor (1-3)."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_SLEVEL, "Уровень загрязнения", "mdi:water-percent"
        )
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        level_map = {"1": "Низкий", "2": "Средний", "3": "Высокий"}
        return level_map.get(value, value)


class BiancaTemperatureSensor(BiancaBaseSensor):
    """Temperature sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_TEMP, "Температура стирки", "mdi:thermometer",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            unit=UnitOfTemperature.CELSIUS,
        )


class BiancaSpinSpeedSensor(BiancaBaseSensor):
    """Spin speed sensor (value × 100 = RPM)."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_SPINSP, "Скорость отжима", "mdi:sync",
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT,
            unit=UnitOfFrequency.REVOLUTIONS_PER_MINUTE,
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
    """Remaining time sensor (seconds)."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_REMTIME, "Оставшееся время", "mdi:timer-outline",
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            unit=UnitOfTime.SECONDS,
        )


class BiancaDelayStartSensor(BiancaBaseSensor):
    """Delay start sensor (seconds)."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_DELVAL, "Отложенный старт", "mdi:calendar-clock",
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            unit=UnitOfTime.SECONDS,
        )


class BiancaLanguageSensor(BiancaBaseSensor):
    """Language sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry):
        super().__init__(
            coordinator, entry, KEY_LANG, "Язык дисплея", "mdi:translate"
        )

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return LANG_MAP.get(value, value)
