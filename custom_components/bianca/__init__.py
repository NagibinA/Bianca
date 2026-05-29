async def async_register_custom_icons(hass: HomeAssistant) -> None:
    """Register custom icons from integration folder."""
    if hasattr(hass.data, "bianca_icons_registered"):
        return
    
    icons_path = hass.config.path("custom_components/bianca/bianca-icons.js")
    
    if not os.path.exists(icons_path):
        _LOGGER.warning("Icon file not found: %s", icons_path)
        return
    
    from homeassistant.components.frontend import add_extra_js_url
    
    www_icons_path = hass.config.path("www/community/bianca-icons.js")
    if not os.path.exists(www_icons_path):
        try:
            os.makedirs(os.path.dirname(www_icons_path), exist_ok=True)
            import shutil
            shutil.copy2(icons_path, www_icons_path)
            _LOGGER.info("Copied icons to %s", www_icons_path)
        except Exception as e:
            _LOGGER.error("Failed to copy icons: %s", e)
            return
    
    add_extra_js_url(hass, "/local/community/bianca-icons.js")
    hass.data["bianca_icons_registered"] = True
    _LOGGER.info("Registered custom icons for Bianca")
