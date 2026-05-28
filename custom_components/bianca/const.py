"""Constants for the Bianca integration."""

DOMAIN = "bianca"
DEFAULT_NAME = "Bianca"
DEFAULT_SCAN_INTERVAL = 25  # seconds (between 20-30 as requested)

PLATFORMS = ["sensor", "binary_sensor"]

CONF_IP_ADDRESS = "ip_address"

# API endpoint
API_ENDPOINT = "http://{}/http-read.json?encrypted=0"

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

# Option names (Opt1 - Opt9)
OPTION_NAMES = {
    "Opt1": "Предварительная стирка",
    "Opt2": "Гигиеническая стирка",
    "Opt3": "Анти сминание",
    "Opt4": "Ночной отжим",
    "Opt5": "Полоскание 1",
    "Opt6": "Полоскание 2",
    "Opt7": "Полоскание 3",
    "Opt8": "Акваплюс",
    "Opt9": "Режим ZOOM",
}

# Sensor keys (for data extraction)
KEY_WIFISTATUS = "WiFiStatus"
KEY_ERR = "Err"
KEY_MACHMD = "MachMd"
KEY_PR = "Pr"
KEY_PRPH = "PrPh"
KEY_SLEVEL = "SLevel"
KEY_TEMP = "Temp"
KEY_SPINSP = "SpinSp"
KEY_REMTIME = "RemTime"
KEY_DELVAL = "DelVal"
KEY_STEAM = "Steam"
KEY_LANG = "Lang"

# All opt keys
OPT_KEYS = [f"Opt{i}" for i in range(1, 10)]
