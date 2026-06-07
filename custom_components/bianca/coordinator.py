"""Data update coordinator for Bianca integration."""

import json
import logging
from datetime import timedelta

import async_timeout
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, API_ENDPOINT, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class BiancaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the device."""

    def __init__(self, hass, ip_address: str, entry_id: str):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.ip_address = ip_address
        self._url = API_ENDPOINT.format(ip_address)
        self._last_valid_data = None
        self._entry_id = entry_id
        self._api_response_status = "NO RESPONSE"

    @property
    def device_available(self) -> bool:
        return self.hass.data.get(DOMAIN, {}).get(self._entry_id, {}).get("available", False)
    
    @property
    def api_response_status(self) -> str:
        return self._api_response_status

    async def _async_update_data(self) -> dict:
        if not self.device_available:
            raise UpdateFailed("Device is offline")
        
        session = async_get_clientsession(self.hass)
        
        try:
            async with async_timeout.timeout(10):
                async with session.get(self._url) as response:
                    if response.status == 200:
                        text = await response.text()
                        try:
                            data = json.loads(text)
                            if "response" in data:
                                self._api_response_status = data["response"]
                                if self._last_valid_data is not None:
                                    return self._last_valid_data
                                raise UpdateFailed(f"API error: {self._api_response_status}")
                            if "statusLavatrice" in data:
                                self._api_response_status = "OK"
                                self._last_valid_data = data.get("statusLavatrice", {})
                                return self._last_valid_data
                            else:
                                self._api_response_status = "UNKNOWN FORMAT"
                                if self._last_valid_data is not None:
                                    return self._last_valid_data
                                raise UpdateFailed("Unknown response format from device")
                        except json.JSONDecodeError:
                            self._api_response_status = "PARSE ERROR"
                            if self._last_valid_data is not None:
                                return self._last_valid_data
                            raise UpdateFailed("JSON decode error")
                    else:
                        self._api_response_status = f"HTTP {response.status}"
                        if self._last_valid_data is not None:
                            return self._last_valid_data
                        raise UpdateFailed(f"HTTP error {response.status}")
        except Exception as e:
            if self.device_available and self._last_valid_data is not None:
                return self._last_valid_data
            raise UpdateFailed(f"Error fetching data: {e}")