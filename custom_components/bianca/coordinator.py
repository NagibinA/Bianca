"""Data coordinator for Bianca integration."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN, API_ENDPOINT, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class BiancaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Bianca device."""

    def __init__(self, hass: HomeAssistant, ip_address: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.ip_address = ip_address
        self._url = API_ENDPOINT.format(ip_address)

    async def _async_update_data(self) -> dict:
        """Fetch data from the device."""
        session = aiohttp_client.async_get_clientsession(self.hass)
        
        try:
            _LOGGER.debug("Fetching data from %s", self._url)
            async with session.get(self._url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("Received data: %s", data)
                    return data.get("statusLavatrice", {})
                else:
                    raise UpdateFailed(f"HTTP error {response.status}")
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}")
