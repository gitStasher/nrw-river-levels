from .const import DOMAIN, UPDATE_INTERVAL, API_BASE_URL, API_STATIONDATA_EP
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed
from datetime import timedelta
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
import random

_LOGGER = logging.getLogger(__name__)

class NaturalResourcesWalesCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

        self.entry = entry
        self.apiKey = entry.data.get("apiKey")
        self.stationId = entry.data.get("stationId")
        self.station = entry.data.get("station")
        self.riverLevelParam = entry.data.get("riverLevelParam")

    async def _async_update_data(self) -> dict[str, Any]:
        
        url = f"{API_BASE_URL}{API_STATIONDATA_EP}/historical?location={self.stationId}&parameter={self.riverLevelParam}"
        session = async_get_clientsession(self.hass)
        
        try:
            response = await session.get(url, headers={"Ocp-Apim-Subscription-Key": self.apiKey})
        except Exception as err:
            raise UpdateFailed(f"Request failed: {err}") from err
        
        if response.status == 401:
            raise ConfigEntryAuthFailed("API key expired or invalid")
        elif response.status != 200:
            raise UpdateFailed(f"API request failed with status {response.status}")

        return await response.json()
