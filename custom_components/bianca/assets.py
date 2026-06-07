"""Assets registration for Bianca integration."""

import json
import os
import shutil
import asyncio
import logging
from homeassistant.components.frontend import add_extra_js_url

from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)


async def async_register_assets(hass):
    """Register custom icons and dashboard strategy."""
    if hasattr(hass.data, "bianca_assets_registered"):
        return
    
    icons_path = hass.config.path(f"custom_components/{DOMAIN}/bianca-icons.js")
    if not os.path.exists(icons_path):
        return
    
    www_dir = hass.config.path("www/community/bianca")
    www_icons_path = hass.config.path("www/community/bianca/bianca-icons.js")
    version_file_path = hass.config.path("www/community/bianca/version.txt")
    
    manifest_path = hass.config.path(f"custom_components/{DOMAIN}/manifest.json")
    current_version = VERSION
    try:
        def read_manifest():
            with open(manifest_path, "r") as f:
                return json.load(f)
        manifest = await hass.async_add_executor_job(read_manifest)
        current_version = manifest.get("version", VERSION)
    except Exception:
        pass
    
    need_copy = False
    if not os.path.exists(www_icons_path):
        need_copy = True
    elif os.path.exists(version_file_path):
        try:
            def read_version():
                with open(version_file_path, "r") as f:
                    return f.read().strip()
            saved_version = await hass.async_add_executor_job(read_version)
            if saved_version != current_version:
                need_copy = True
        except Exception:
            need_copy = True
    else:
        need_copy = True
    
    if need_copy:
        try:
            def copy_icons():
                os.makedirs(www_dir, exist_ok=True)
                shutil.copy2(icons_path, www_icons_path)
                with open(version_file_path, "w") as f:
                    f.write(current_version)
            await hass.async_add_executor_job(copy_icons)
        except Exception:
            return
    
    # original.png в папке brand
    machine_image_src = hass.config.path(f"custom_components/{DOMAIN}/brand/original.png")
    machine_image_dest = hass.config.path("www/community/bianca/original.png")
    if os.path.exists(machine_image_src):
        try:
            if need_copy or not os.path.exists(machine_image_dest):
                def copy_image():
                    shutil.copy2(machine_image_src, machine_image_dest)
                await hass.async_add_executor_job(copy_image)
        except Exception:
            pass
    
    dashboard_js_src = hass.config.path(f"custom_components/{DOMAIN}/dashboard/bianca-dashboard.js")
    dashboard_js_dest = hass.config.path("www/community/bianca/bianca-dashboard.js")
    if os.path.exists(dashboard_js_src):
        try:
            if need_copy or not os.path.exists(dashboard_js_dest):
                def copy_dashboard():
                    os.makedirs(www_dir, exist_ok=True)
                    shutil.copy2(dashboard_js_src, dashboard_js_dest)
                await hass.async_add_executor_job(copy_dashboard)
        except Exception:
            pass
    
    simple_js_src = hass.config.path(f"custom_components/{DOMAIN}/dashboard/bianca-simple.js")
    simple_js_dest = hass.config.path("www/community/bianca/bianca-simple.js")
    if os.path.exists(simple_js_src):
        try:
            if need_copy or not os.path.exists(simple_js_dest):
                def copy_simple():
                    os.makedirs(www_dir, exist_ok=True)
                    shutil.copy2(simple_js_src, simple_js_dest)
                await hass.async_add_executor_job(copy_simple)
                _LOGGER.info("Copied bianca-simple.js to %s", simple_js_dest)
        except Exception as e:
            _LOGGER.error("Failed to copy bianca-simple.js: %s", e)
    
    # admin.html в папке www
    admin_html_src = hass.config.path(f"custom_components/{DOMAIN}/www/admin.html")
    admin_html_dest = hass.config.path("www/community/bianca/admin.html")
    if os.path.exists(admin_html_src):
        try:
            if need_copy or not os.path.exists(admin_html_dest):
                def copy_admin():
                    os.makedirs(www_dir, exist_ok=True)
                    shutil.copy2(admin_html_src, admin_html_dest)
                await hass.async_add_executor_job(copy_admin)
                _LOGGER.info("Copied admin HTML to %s", admin_html_dest)
        except Exception as e:
            _LOGGER.error("Failed to copy admin HTML: %s", e)
    
    # Регистрируем JS файлы
    if "bianca_assets_registered" not in hass.data:
        try:
            add_extra_js_url(hass, "/local/community/bianca/bianca-icons.js")
            add_extra_js_url(hass, "/local/community/bianca/bianca-dashboard.js")
            add_extra_js_url(hass, "/local/community/bianca/bianca-simple.js")
        except Exception:
            return
    
    hass.data["bianca_assets_registered"] = True
    _LOGGER.info("Bianca assets registered")