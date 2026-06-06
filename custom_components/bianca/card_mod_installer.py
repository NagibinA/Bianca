"""Card Mod installer for Bianca integration.  2.4.2"""

import logging
import os
import shutil
import asyncio
import aiohttp
from homeassistant.components.frontend import add_extra_js_url

_LOGGER = logging.getLogger(__name__)

CARD_MOD_URL = "https://raw.githubusercontent.com/thomasloven/lovelace-card-mod/master/card-mod.js"
CARD_MOD_FILE = "card-mod.js"
CARD_MOD_PATH = "community/lovelace-card-mod"  # правильный путь без www/


async def ensure_card_mod(hass):
    """Проверяет наличие Card Mod и устанавливает при отсутствии."""
    
    card_mod_installed = await _is_card_mod_installed(hass)
    
    if card_mod_installed:
        _LOGGER.info("Card Mod already installed")
        return True
    
    _LOGGER.info("Card Mod not found, installing...")
    
    success = await _install_card_mod(hass)
    
    if success:
        _LOGGER.info("Card Mod installed successfully")
    else:
        _LOGGER.warning("Failed to install Card Mod. Please install manually from HACS")
    
    return success


async def _is_card_mod_installed(hass):
    """Проверяет наличие Card Mod (асинхронно)."""
    
    # 1. Проверка через ресурсы Lovelace
    try:
        if "lovelace" in hass.data and "resources" in hass.data["lovelace"]:
            resources = hass.data["lovelace"]["resources"].async_items()
            for resource in resources:
                if "card-mod" in resource.get("url", "").lower():
                    _LOGGER.debug("Card Mod found in Lovelace resources")
                    return True
    except Exception as e:
        _LOGGER.debug(f"Error checking Lovelace resources: {e}")
    
    # 2. Проверка через configuration.yaml (игнорируем закомментированные строки)
    try:
        config_path = hass.config.path("configuration.yaml")
        if os.path.exists(config_path):
            def read_config():
                with open(config_path, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        if "card-mod.js" in stripped:
                            return True
                return False
            found = await hass.async_add_executor_job(read_config)
            if found:
                _LOGGER.debug("Card Mod found in configuration.yaml")
                return True
    except Exception as e:
        _LOGGER.debug(f"Error checking configuration.yaml: {e}")
    
    # 3. Проверка наличия файла в www
    local_path = hass.config.path(f"www/{CARD_MOD_PATH}/{CARD_MOD_FILE}")
    if os.path.exists(local_path):
        _LOGGER.debug("Card Mod file exists in www")
        return True
    
    # 4. Проверка через установленные ресурсы extra_module_url
    try:
        frontend_conf = hass.data.get("frontend", {})
        extra_urls = frontend_conf.get("extra_module_url", [])
        for url in extra_urls:
            if "card-mod" in url.lower():
                _LOGGER.debug("Card Mod found in extra_module_url")
                return True
    except Exception as e:
        _LOGGER.debug(f"Error checking extra_module_url: {e}")
    
    return False


async def _install_card_mod(hass):
    """Устанавливает Card Mod (асинхронно)."""
    
    # Создаём директорию
    dest_dir = hass.config.path(f"www/{CARD_MOD_PATH}")
    dest_file = hass.config.path(f"www/{CARD_MOD_PATH}/{CARD_MOD_FILE}")
    
    def make_dirs():
        os.makedirs(dest_dir, exist_ok=True)
    
    try:
        await hass.async_add_executor_job(make_dirs)
    except Exception as e:
        _LOGGER.error(f"Failed to create directory {dest_dir}: {e}")
        return False
    
    # Скачиваем с официального репозитория
    downloaded = await _download_card_mod(hass, dest_file)
    
    if not downloaded:
        # Если скачать не удалось, пробуем скопировать встроенную копию
        embedded_path = hass.config.path(f"custom_components/bianca/www/{CARD_MOD_FILE}")
        if os.path.exists(embedded_path):
            try:
                def copy_file():
                    shutil.copy2(embedded_path, dest_file)
                await hass.async_add_executor_job(copy_file)
                _LOGGER.info("Card Mod copied from embedded file")
                downloaded = True
            except Exception as e:
                _LOGGER.error(f"Failed to copy embedded Card Mod: {e}")
    
    if not downloaded:
        return False
    
    # Регистрируем ресурс через API Lovelace
    try:
        await _register_card_mod_resource(hass)
        _LOGGER.info("Card Mod registered as resource")
    except Exception as e:
        _LOGGER.error(f"Failed to register Card Mod resource: {e}")
        # Пробуем альтернативный метод
        try:
            add_extra_js_url(hass, f"/local/{CARD_MOD_PATH}/{CARD_MOD_FILE}")
            _LOGGER.info("Card Mod registered via add_extra_js_url")
        except Exception as e2:
            _LOGGER.error(f"Alternative registration also failed: {e2}")
            return False
    
    return True


async def _register_card_mod_resource(hass):
    """Регистрирует Card Mod как ресурс Lovelace через API."""
    
    resource_url = f"/local/{CARD_MOD_PATH}/{CARD_MOD_FILE}"  # /local/community/lovelace-card-mod/card-mod.js
    
    # Ждём готовности Lovelace
    for _ in range(10):
        if "lovelace" in hass.data and hasattr(hass.data["lovelace"], "resources"):
            break
        await asyncio.sleep(1)
    else:
        _LOGGER.warning("Lovelace not ready, Card Mod resource not registered")
        return
    
    lovelace = hass.data["lovelace"]
    
    # Проверяем, не добавлен ли уже
    existing_resources = lovelace.resources.async_items()
    for resource in existing_resources:
        if resource.get("url") == resource_url:
            _LOGGER.debug("Card Mod resource already exists")
            return
    
    # Добавляем ресурс
    await lovelace.resources.async_create_item({
        "res_type": "module",
        "url": resource_url
    })
    _LOGGER.info(f"Card Mod resource added: {resource_url}")


async def _download_card_mod(hass, dest_file):
    """Скачивает Card Mod с GitHub."""
    
    session = None
    try:
        session = aiohttp.ClientSession()
        async with session.get(CARD_MOD_URL) as response:
            if response.status == 200:
                content = await response.text()
                
                def write_file():
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                await hass.async_add_executor_job(write_file)
                _LOGGER.info(f"Card Mod downloaded from {CARD_MOD_URL}")
                return True
            else:
                _LOGGER.error(f"Failed to download Card Mod: HTTP {response.status}")
                return False
    except Exception as e:
        _LOGGER.error(f"Error downloading Card Mod: {e}")
        return False
    finally:
        if session:
            await session.close()
