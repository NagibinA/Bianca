"""Data coordinator for Bianca integration."""

import asyncio
import logging
from datetime import timedelta

import aiohttp
import async_timeout
from backoff import on_exception, expo
from aiolimiter import AsyncLimiter

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

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
        self._limiter = AsyncLimiter(1, time_period=1)  # 1 request per second
        self._url = API_ENDPOINT.format(ip_address)

    @on_exception(expo, aiohttp.ClientError, max_tries=3)
    async def _fetch_data(self) -> dict:
        """Fetch data from the device."""
        async with self._limiter:
            try:
                async with async_timeout.timeout(10):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(self._url) as response:
                            if response.status == 200:
                                data = await response.json()
                                return data.get("statusLavatrice", {})
                            else:
                                raise UpdateFailed(
                                    f"HTTP error {response.status} from {self._url}"
                                )
            except asyncio.TimeoutError:
                raise UpdateFailed(f"Timeout connecting to {self._url}")
            except aiohttp.ClientError as err:
                raise UpdateFailed(f"Error connecting to {self._url}: {err}")

    async def _async_update_data(self) -> dict:
        """Fetch data from the device."""
        try:
            data = await self._fetch_data()
            _LOGGER.debug("Fetched data from Bianca: %s", data)
            return data
        except UpdateFailed as err:
            _LOGGER.error("Update failed: %s", err)
            raise
