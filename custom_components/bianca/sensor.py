"""Sensor platform for Bianca integration - Version 2.6.3."""

from __future__ import annotations
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    CONF_IP_ADDRESS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    MACHMD_MAP,
    PR_MAP,
    PRPH_MAP,
    ERR_MAP,
    LANG_MAP,
    SOIL_LEVEL_MAP,
)
from .coordinator import BiancaDataUpdateCoordinator


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
        # DIAGNOSTIC (будут в настройках -> диагностика)
        BiancaApiReadStatusSensor(coordinator, entry, hass),
        BiancaApiWriteStatusSensor(coordinator, entry, hass),
        BiancaFinishTimeSensor(coordinator, entry, hass),
        BiancaLanguageSensor(coordinator, entry, hass),
        BiancaPreWashSensor(coordinator, entry, hass),
        BiancaHygienicSensor(coordinator, entry, hass),
        BiancaAntiCreaseSensor(coordinator, entry, hass),
        BiancaNightSpinSensor(coordinator, entry, hass),
        BiancaRinseSensor(coordinator, entry, hass),
        BiancaAquaPlusSensor(coordinator, entry, hass),
        BiancaZoomSensor(coordinator, entry, hass),
        BiancaRemoteControlSensor(coordinator, entry, hass),
        BiancaErrorSensor(coordinator, entry, hass),
        BiancaSoilLevelSensor(coordinator, entry, hass),
        BiancaSteamSensor(coordinator, entry, hass),
        BiancaDelayStartSensor(coordinator, entry, hass),
        BiancaRemainingTimeSensor(coordinator, entry, hass),
        
        # Основные (будут на панели "Обзор")
        BiancaMachineStateSensor(coordinator, entry, hass),
        BiancaProgramSensor(coordinator, entry, hass),
        BiancaProgramPhaseSensor(coordinator, entry, hass),
        BiancaTemperatureSensor(coordinator, entry, hass),
        BiancaSpinSpeedSensor(coordinator, entry, hass),
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
        super().__init__(coordinator)
        self._key = key
        self._entry = entry
        self._hass = hass
        self.entity_id = f"sensor.bianca_{entity_id_key}"
        self._attr_unique_id = f"{entry.entry_id}_sensor_{entity_id_key}"
        self._attr_name = f"Bianca {display_name}"
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])}}

    @property
    def available(self) -> bool:
        if not self.coordinator.device_available:
            return False
        if self.coordinator.data is None:
            return False
        return True

    @property
    def native_value(self):
        if not self.coordinator.device_available:
            return None
        if self.coordinator.data is None:
            return None
        if self._key is None:
            return None
        return self.coordinator.data.get(self._key)


class BiancaApiReadStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for API read status."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator)
        self._entry = entry
        self._hass = hass
        self.entity_id = "sensor.bianca_api_read_status"
        self._attr_unique_id = f"{entry.entry_id}_sensor_api_read_status"
        self._attr_name = "Bianca Статус чтения API"
        self._attr_icon = "mdi:api"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])}}

    @property
    def available(self) -> bool:
        if not self.coordinator.device_available:
            return False
        return True

    @property
    def native_value(self) -> str:
        return self.coordinator.api_read_status


class BiancaApiWriteStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for API write status."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator)
        self._entry = entry
        self._hass = hass
        self.entity_id = "sensor.bianca_api_write_status"
        self._attr_unique_id = f"{entry.entry_id}_sensor_api_write_status"
        self._attr_name = "Bianca Статус записи API"
        self._attr_icon = "mdi:api"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._entry.data[CONF_IP_ADDRESS])}}

    @property
    def available(self) -> bool:
        if not self.coordinator.device_available:
            return False
        return True

    @property
    def native_value(self) -> str:
        return self.coordinator.api_write_status


class BiancaRemoteControlSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "WiFiStatus", "remote_control", "Удаленное управление", "mdi:wifi")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        value = super().native_value
        if value == "1":
            return "Вкл"
        elif value == "0":
            return "Выкл"
        return value


class BiancaErrorSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "Err", "error", "Ошибка", "mdi:alert-circle")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        if value == "0":
            return "Нет ошибок"
        return ERR_MAP.get(value, f"Неизвестная ошибка ({value})")


class BiancaMachineStateSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "MachMd", "machine_state", "Состояние машины", "mdi:washing-machine")

    @property
    def available(self) -> bool:
        return True

    @property
    def native_value(self):
        if not self.coordinator.device_available:
            return "Выключена"
        
        value = super().native_value
        if value is None:
            return "Выключена"
        return MACHMD_MAP.get(value, value)


class BiancaProgramSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "Pr", "program", "Программа стирки", "mdi:format-list-bulleted")

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return PR_MAP.get(value, value)

    @property
    def extra_state_attributes(self):
        if self.coordinator.data is None:
            return {}
        return {"program_number": self.coordinator.data.get("Pr")}


class BiancaProgramPhaseSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "PrPh", "program_phase", "Фаза программы", "mdi:progress-clock")

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return PRPH_MAP.get(value, value)


class BiancaSoilLevelSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "SLevel", "soil_level", "Уровень загрязнения", "mdi:water-percent")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
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
        if self.coordinator.data is None:
            return "mdi:help-circle-outline"
        value = self.coordinator.data.get("SLevel")
        if value == "1":
            return "bianca:duco-1"
        elif value == "2":
            return "bianca:duco-2"
        elif value == "3":
            return "bianca:duco-3"
        return "mdi:help-circle-outline"


class BiancaTemperatureSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass, "Temp", "temperature", "Температура стирки", "mdi:thermometer",
            device_class=None,
            state_class=SensorStateClass.MEASUREMENT,
            unit=None
        )

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return value


class BiancaSpinSpeedSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass, "SpinSp", "spin_speed", "Скорость отжима", "mdi:rotate-right",
            state_class=SensorStateClass.MEASUREMENT,
            unit=None
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
    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass, "RemTime", "remaining_time", "Оставшееся время", "mdi:timer-outline",
            unit=None
        )
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
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
    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass, "DelVal", "delay_start", "Отложенный старт", "mdi:timer-outline",
            unit=None
        )
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return ""
        machine_state = self.coordinator.data.get("MachMd")
        if machine_state != "5":
            return ""
        value = self.coordinator.data.get("DelVal")
        if value is None:
            return ""
        try:
            minutes = int(value)
            if minutes <= 0:
                return ""
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours:02d}:{mins:02d}"
        except (ValueError, TypeError):
            return ""


class BiancaLanguageSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "Lang", "language", "Язык дисплея", "mdi:translate")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        value = super().native_value
        if value is None:
            return None
        return LANG_MAP.get(value, value)


class BiancaSteamSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "Steam", "steam", "Пар", "bianca:steam")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaPreWashSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "Opt1", "pre_wash", "Предварительная стирка", "bianca:pre-wash")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaHygienicSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "Opt2", "hygienic_wash", "Гигиеническая стирка", "bianca:hygiene-wash")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaAntiCreaseSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "Opt3", "anti_crease", "Анти сминание", "bianca:anti-crease")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaNightSpinSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "Opt4", "night_spin", "Ночной отжим", "bianca:night-spin")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaRinseSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, None, "rinse", "Полоскание", "mdi:water-off")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
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
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "Opt8", "aqua_plus", "Акваплюс", "bianca:extra-water")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaZoomSensor(BiancaBaseSensor):
    def __init__(self, coordinator, entry, hass):
        super().__init__(coordinator, entry, hass, "Opt9", "zoom", "Режим ZOOM", "bianca:zoom")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        value = super().native_value
        return "Включен" if value == "1" else "Выключен"


class BiancaFinishTimeSensor(BiancaBaseSensor):
    """Sensor for washing completion time."""

    def __init__(self, coordinator, entry, hass):
        super().__init__(
            coordinator, entry, hass, "RemTime", "finish_time", 
            "Время окончания", "mdi:timer-sand",
            device_class=SensorDeviceClass.TIMESTAMP
        )
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        
        machine_state = self.coordinator.data.get("MachMd")
        
        # Режим отложенного старта
        if machine_state == "5":
            del_val = self.coordinator.data.get("DelVal")
            rem_time = self.coordinator.data.get("RemTime")
            
            if del_val is None or rem_time is None:
                return None
            
            try:
                delay_minutes = int(del_val)
                wash_seconds = int(rem_time)
                total_seconds = (delay_minutes * 60) + wash_seconds
                if total_seconds <= 0:
                    return None
                finish_time = dt_util.now() + timedelta(seconds=total_seconds)
                return finish_time
            except (ValueError, TypeError):
                return None
        
        # Режим работы или пауза
        if machine_state in ["2", "3"]:
            rem_time = self.coordinator.data.get("RemTime")
            if rem_time is None:
                return None
            try:
                seconds = int(rem_time)
                if seconds <= 0:
                    return None
                finish_time = dt_util.now() + timedelta(seconds=seconds)
                return finish_time
            except (ValueError, TypeError):
                return None
        
        return None
