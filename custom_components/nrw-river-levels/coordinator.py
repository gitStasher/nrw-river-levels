from .const import DOMAIN, UPDATE_INTERVAL, API_BASE_URL, API_STATIONDATA_EP
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed
)
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
        self.api_key = entry.data.get("api_key")

    async def _async_update_data(self) -> dict[str, Any]:
        url = f"{API_BASE_URL}{API_STATIONDATA_EP}"
        session = async_get_clientsession(self.hass)

        try:
            response = await session.get(
                url,
                headers={"Ocp-Apim-Subscription-Key": self.api_key}
            )
        except Exception as err:
            raise UpdateFailed(f"Request failed: {err}") from err

        if response.status == 401:
            raise ConfigEntryAuthFailed("API key expired or invalid")
        elif response.status == 403:
            if "Out of call volume quota" in (
                msg := (await response.json()).get("message", "")
            ):
                raise UpdateFailed(f"API rate limit exceeded: {msg}")
            else:
                raise UpdateFailed("unknown")
        elif response.status != 200:
            raise UpdateFailed(
                f"API request failed with status {response.status}"
            )

        data = await response.json()
        selected_ids = {int(s) for s in self.entry.data.get("stations", [])}
        filtered = [s for s in data if int(s["stationId"]) in selected_ids]
        return {"stations": {s["stationId"]: s for s in filtered}}
