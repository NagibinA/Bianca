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
    CONF_IP_ADDRESS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MACHMD_MAP,
    PR_MAP,
    PRPH_MAP,
    ERR_MAP,
    LANG_MAP,
    SOIL_LEVEL_MAP,
)
from . import BiancaDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bianca sensors."""
    coordinator: BiancaDataUpdateCoordinator = entry.runtime_data
    
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator
    
    entities = [
        BiancaApiResponseSensor(coordinator, entry, hass),
        BiancaRemoteControlSensor(coordinator, entry, hass),
        BiancaErrorSensor(coordinator, entry, hass),
        BiancaMachineStateSensor(coordinator, entry, hass),
        BiancaProgramSensor(coordinator, entry, hass),
        BiancaProgramPhaseSensor(coordinator, entry, hass),
        BiancaSoilLevelSensor(coordinator, entry, hass),
        BiancaTemperatureSensor(coordinator, entry, hass),
        BiancaSpinSpeedSensor(coordinator, entry, hass),
        BiancaRemainingTimeSensor(coordinator, entry, hass),
        BiancaDelayStartSensor(coordinator, entry, hass),
        BiancaLanguageSensor(coordinator, entry, hass),
        BiancaSteamSensor(coordinator, entry, hass),
        BiancaPreWashSensor(coordinator, entry, hass),
        BiancaHygienicSensor(coordinator, entry, hass),
        BiancaAntiCreaseSensor(coordinator, entry, hass),
        BiancaNightSpinSensor(coordinator, entry, hass),
        BiancaRinseSensor(coordinator, entry, hass),
        BiancaAquaPlusSensor(coordinator, entry, hass),
        BiancaZoomSensor(coordinator, entry, hass),
    ]
    
    async_add_entities(entities)


class BiancaBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Bianca sensors."""

    def __init__(
        self, 
        coordinator: BiancaDataUpdateCoordinator, 
        entry: ConfigEntry,
        hass: HomeAssistant,
        key: str | None,
        entity_id_key: str,
        display_name: str,
        icon: str,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        unit: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._entry = entry
        self._hass = hass
        self.entity_id = f"sensor.bianca_{entity_id_key}"
        self._attr_name = f"Bianca {display_name}"
        self._attr_unique_id = f"{entry.entry_id}_{entity_id_key}"
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])},
        }
    
    @property
    def _device_available(self) -> bool:
        """Check if device is available via ping."""
        if DOMAIN not in self._hass.data:
            return False
        if self._entry.entry_id not in self._hass.data[DOMAIN]:
            return False
        return self._hass.data[DOMAIN][self._entry.entry_id].get("available", False)

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return self._device_available and super().available

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self._device_available:
            return None
        
        if self.coordinator.data is None:
            return None
        if self._key is None:
            return None
        return self.coordinator.data.get(self._key)


class BiancaApiResponseSensor(CoordinatorEntity, SensorEntity):
    """Sensor for API response status."""

    def __init__(
        self, 
        coordinator: BiancaDataUpdateCoordinator, 
        entry: ConfigEntry,
        hass: HomeAssistant,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._hass = hass
        self.entity_id = "sensor.bianca_api_response"
        self._attr_name = "Bianca Статус API"
        self._attr_unique_id = f"{entry.entry_id}_api_response"
        self._attr_icon = "mdi:api"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])},
        }
    
    @property
    def _device_available(self) -> bool:
        """Check if device is available via ping."""
        if DOMAIN not in self._hass.data:
            return False
        if self._entry.entry_id not in self._hass.data[DOMAIN]:
            return False
        return self._hass.data[DOMAIN][self._entry.entry_id].get("available", False)

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return True

    @property
    def native_value(self) -> str:
        """Return the API response status."""
        if not self._device_available:
            return "NO RESPONSE"
        return self.coordinator.api_response_status


class BiancaRemoteControlSensor(BiancaBaseSensor):
    """Remote control sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "WiFiStatus", "remote_control", "Удаленное управление", "mdi:wifi")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        if value == "1":
            return "Вкл"
        elif value == "0":
            return "Выкл"
        return value


class BiancaErrorSensor(BiancaBaseSensor):
    """Error sensor with text description."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "Err", "error", "Ошибка", "mdi:alert-circle")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        if value is None:
            return None
        if value == "0":
            return "Нет ошибок"
        return ERR_MAP.get(value, f"Неизвестная ошибка ({value})")


class BiancaMachineStateSensor(BiancaBaseSensor):
    """Machine state sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "MachMd", "machine_state", "Состояние машины", "mdi:washing-machine")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        if value is None:
            return None
        return MACHMD_MAP.get(value, value)


class BiancaProgramSensor(BiancaBaseSensor):
    """Program sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "Pr", "program", "Программа стирки", "mdi:format-list-bulleted")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        if value is None:
            return None
        return PR_MAP.get(value, value)

    @property
    def extra_state_attributes(self):
        """Return program number attribute."""
        if not self._device_available or self.coordinator.data is None:
            return {}
        return {"program_number": self.coordinator.data.get("Pr")}


class BiancaProgramPhaseSensor(BiancaBaseSensor):
    """Program phase sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "PrPh", "program_phase", "Фаза программы", "mdi:progress-clock")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        if value is None:
            return None
        return PRPH_MAP.get(value, value)


class BiancaSoilLevelSensor(BiancaBaseSensor):
    """Soil level sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(
            coordinator, entry, hass, "SLevel", "soil_level", "Уровень загрязнения", "mdi:water-percent",
        )

    @property
    def native_value(self):
        if not self._device_available:
            return None
        
        if self.coordinator.data is None:
            return None
        
        value = self.coordinator.data.get("SLevel")
        
        if value is None:
            return None
        
        str_value = str(value)
        
        if str_value == "0":
            return None
        
        return SOIL_LEVEL_MAP.get(str_value, str_value)

    @property
    def icon(self):
        if not self._device_available:
            return "mdi:help-circle-outline"
        
        if self.coordinator.data is None:
            return "mdi:help-circle-outline"
        
        value = self.coordinator.data.get("SLevel")
        
        if value == "1":
            return "phu:duco-1"
        elif value == "2":
            return "phu:duco-2"
        elif value == "3":
            return "phu:duco-3"
        return "mdi:help-circle-outline"


class BiancaTemperatureSensor(BiancaBaseSensor):
    """Temperature sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(
            coordinator, entry, hass, "Temp", "temperature", "Температура стирки", "mdi:thermometer",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            unit=UnitOfTemperature.CELSIUS
        )


class BiancaSpinSpeedSensor(BiancaBaseSensor):
    """Spin speed sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(
            coordinator, entry, hass, "SpinSp", "spin_speed", "Скорость отжима", "bianca:spin",
            state_class=SensorStateClass.MEASUREMENT,
            unit=None
        )

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        if value is None:
            return None
        try:
            return int(value) * 100
        except (ValueError, TypeError):
            return value


class BiancaRemainingTimeSensor(BiancaBaseSensor):
    """Remaining time sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(
            coordinator, entry, hass, "RemTime", "remaining_time", "Оставшееся время", "mdi:timer-outline",
            unit=None
        )

    @property
    def native_value(self):
        if not self._device_available:
            return None
        
        if self.coordinator.data is None:
            return None
        
        machine_state = self.coordinator.data.get("MachMd")
        
        if machine_state not in ["2", "3"]:
            return "00:00"
        
        value = self.coordinator.data.get("RemTime")
        
        if value is None:
            return "00:00"
        
        try:
            seconds = int(value)
            if seconds <= 0:
                return "00:00"
            
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            
            return f"{hours:02d}:{minutes:02d}"
        except (ValueError, TypeError):
            return "00:00"


class BiancaDelayStartSensor(BiancaBaseSensor):
    """Delay start sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(
            coordinator, entry, hass, "DelVal", "delay_start", "Отложенный старт", "bianca:delay",
            unit=None
        )

    @property
    def native_value(self):
        if not self._device_available:
            return None
        
        if self.coordinator.data is None:
            return ""
        
        machine_state = self.coordinator.data.get("MachMd")
        
        if machine_state != "4":
            return ""
        
        value = self.coordinator.data.get("DelVal")
        
        if value is None:
            return ""
        
        try:
            seconds = int(value)
            if seconds <= 0:
                return ""
            
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            
            return f"{hours:02d}:{minutes:02d}"
        except (ValueError, TypeError):
            return ""


class BiancaLanguageSensor(BiancaBaseSensor):
    """Language sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "Lang", "language", "Язык дисплея", "mdi:translate")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        if value is None:
            return None
        return LANG_MAP.get(value, value)


class BiancaSteamSensor(BiancaBaseSensor):
    """Steam sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "Steam", "steam", "Пар", "bianca:steam")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaPreWashSensor(BiancaBaseSensor):
    """Pre-wash sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "Opt1", "pre_wash", "Предварительная стирка", "bianca:pre-wash")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaHygienicSensor(BiancaBaseSensor):
    """Hygienic wash sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "Opt2", "hygienic_wash", "Гигиеническая стирка", "bianca:hygiene-wash")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaAntiCreaseSensor(BiancaBaseSensor):
    """Anti-crease sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "Opt3", "anti_crease", "Анти сминание", "bianca:anti-crease")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaNightSpinSensor(BiancaBaseSensor):
    """Night spin sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "Opt4", "night_spin", "Ночной отжим", "bianca:night-spin")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaRinseSensor(BiancaBaseSensor):
    """Rinse sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(
            coordinator, entry, hass, None, "rinse", "Полоскание", "mdi:water-off",
        )

    @property
    def native_value(self):
        if not self._device_available:
            return None
        
        if self.coordinator.data is None:
            return ""
        
        if self.coordinator.data.get("Opt5") == "1":
            return "Одно"
        elif self.coordinator.data.get("Opt6") == "1":
            return "Два"
        elif self.coordinator.data.get("Opt7") == "1":
            return "Три"
        return ""

    @property
    def icon(self):
        if not self._device_available:
            return "mdi:water-off"
        
        if self.coordinator.data is None:
            return "mdi:water-off"
        
        if self.coordinator.data.get("Opt5") == "1":
            return "bianca:rinse-1"
        elif self.coordinator.data.get("Opt6") == "1":
            return "bianca:rinse-2"
        elif self.coordinator.data.get("Opt7") == "1":
            return "bianca:rinse-3"
        return "mdi:water-off"


class BiancaAquaPlusSensor(BiancaBaseSensor):
    """Aqua plus sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "Opt8", "aqua_plus", "Акваплюс", "bianca:extra-water")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaZoomSensor(BiancaBaseSensor):
    """Zoom sensor."""

    def __init__(self, coordinator: BiancaDataUpdateCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry, hass, "Opt9", "zoom", "Режим ZOOM", "bianca:zoom")

    @property
    def native_value(self):
        if not self._device_available:
            return None
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"
