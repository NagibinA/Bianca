"""Data coordinator for Bianca integration."""

import asyncio
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
        self._session = None

    @property
    def session(self):
        """Get the client session."""
        if self._session is None:
            self._session = aiohttp_client.async_get_clientsession(self.hass)
        return self._session

    async def _async_update_data(self) -> dict:
        """Fetch data from the device."""
        try:
            async with asyncio.timeout(10):
                _LOGGER.debug("Fetching data from %s", self._url)
                async with self.session.get(self._url) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("Received data: %s", data)
                        return data.get("statusLavatrice", {})
                    else:
                        _LOGGER.warning("HTTP error %s from %s", response.status, self._url)
                        raise UpdateFailed(f"HTTP error {response.status}")
        except TimeoutError:
            _LOGGER.warning("Timeout connecting to %s", self._url)
            raise UpdateFailed("Timeout connecting to device")
        except Exception as err:
            _LOGGER.warning("Error connecting to %s: %s", self._url, err)
            raise UpdateFailed(f"Connection error: {err}")
