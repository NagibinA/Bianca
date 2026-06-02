"""Constants for the Bianca integration."""

import json
import os
import asyncio
import logging
from typing import Any

DOMAIN = "bianca"
CONF_INTEGRATION_TITLE = "Bianca"
DEFAULT_SCAN_INTERVAL = 30
VERSION = "2.1.0"

CONF_IP_ADDRESS = "ip_address"

API_ENDPOINT = "http://{}/http-read.json?encrypted=0"

PLATFORMS = ["sensor", "binary_sensor", "select"]

# Путь к файлу конфигурации программ
PROGRAMS_CONFIG_FILE = "programs.json"

# Опции и их соответствие entity_id
OPTION_TO_ENTITY = {
    "temperature": "select.bianca_temperature",
    "spin": "select.bianca_spin",
    "soil": "select.bianca_soil",
    "steam": "select.bianca_steam",
    "pre_wash": "select.bianca_pre_wash",
    "hygiene": "select.bianca_hygiene",
    "anti_crease": "select.bianca_anti_crease",
    "night_spin": "select.bianca_night_spin",
    "extra_rinse": "select.bianca_extra_rinse",
    "aqua_plus": "select.bianca_aqua_plus",
    "zoom": "select.bianca_zoom",
}

# Обратное отображение entity_id -> option
ENTITY_TO_OPTION = {v: k for k, v in OPTION_TO_ENTITY.items()}

# MachMd (machine mode) mapping
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

# Pr (program) mapping
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

# PrPh (program phase) mapping
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

# Err (error) mapping
ERR_MAP = {
    "0": "Нет ошибок",
    "2": "Машина не может набрать воду",
    "3": "Стиральная машина не сливает воду",
    "4": "Слишком много пены и/или воды",
    "7": "Проблема с дверцей",
}

# Lang mapping
LANG_MAP = {
    "7": "Русский",
}

# Soil level mapping
SOIL_LEVEL_MAP = {
    "1": "Мало",
    "2": "Нормально",
    "3": "Очень",
}

# Словарь для преобразования значений опций в коды API
OPTION_VALUE_TO_CODE = {
    "pre_wash": {"Нет": 0, "Есть": 1},
    "hygiene": {"Нет": 0, "Есть": 2},
    "anti_crease": {"Нет": 0, "Есть": 4},
    "night_spin": {"Нет": 0, "Есть": 8},
    "extra_rinse": {
        "Нет": 0,
        "1 полоскание": 16,
        "2 полоскания": 32,
        "3 полоскания": 64,
    },
    "aqua_plus": {"Нет": 0, "Есть": 128},
    "zoom": {"Нет": 0, "Есть": 1},
    "steam": {"Без пара": 0, "С паром": 5},
}

_LOGGER = logging.getLogger(__name__)


async def load_programs_config(hass) -> dict[str, Any]:
    """Загружает конфигурацию программ из JSON файла (асинхронно)."""
    import asyncio
    
    config_path = hass.config.path(f"custom_components/{DOMAIN}/{PROGRAMS_CONFIG_FILE}")
    
    if not os.path.exists(config_path):
        _LOGGER.error(f"Programs config file not found: {config_path}")
        return {}
    
    try:
        def read_file():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        return await asyncio.to_thread(read_file)
    except Exception as e:
        _LOGGER.error(f"Failed to load programs config: {e}")
        return {}
