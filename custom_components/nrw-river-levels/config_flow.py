import voluptuous as vol
from typing import Mapping, Any, List, Dict
from homeassistant.helpers import device_registry as dr
from .errors import InvalidAuth, CannotConnect
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector
from homeassistant.config_entries import (
    ConfigFlowResult,
    ConfigFlow,
)

from .const import DOMAIN, API_BASE_URL, API_STATIONDATA_EP, RIVER_LEVEL
import logging

_LOGGER = logging.getLogger(__name__)


class NaturalResourcesWalesRiverLevelsConfigFlow(
    ConfigFlow,
    domain=DOMAIN
):

    VERSION = 2
    MINOR_VERSION = 2

    def __init__(self):
        self.api_key = None

    def get_api_schema(self) -> vol.Schema:
        """Returns the Schema for forms where an API key is required"""
        return vol.Schema({
            vol.Required("api_key"): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD
                )
            ),
        })

    def get_river_list_schema(self, options) -> vol.Schema:
        """Returns the schema for the river selection form"""
        return vol.Schema(
            {
                vol.Required("station"): vol.In(options)
            }
        )

    def get_initial_menu_options(self) -> List[str]:
        """Returns the initial options the user is to select"""
        return ["riverlevel", "floodalert"]

    async def fetch_station_data(self, api_key: str) -> dict:
        """This gets a list of stations using the API key provided"""
        session = async_get_clientsession(self.hass)
        url = f"{API_BASE_URL}{API_STATIONDATA_EP}"
        response = await session.get(
            url,
            headers={"Ocp-Apim-Subscription-Key": api_key}
        )

        if response.status == 200:
            self.api_key = api_key
            station_data = await self.filter_river_stations(
                await response.json()
            )
            device_reg = dr.async_get(self.hass)
            existing_station_ids = {
                next(
                    iter(i for i in dev.identifiers if i[0] == DOMAIN),
                    (None, None)
                )[1]
                for dev in device_reg.devices.values()
                if any(i[0] == DOMAIN for i in dev.identifiers or {})
            }
            options = [
                f'{station["title"]} ({station["id"]})'
                for station in station_data
                if station["id"] not in existing_station_ids
            ]
            return options
        elif response.status == 401:
            raise InvalidAuth("invalid_auth")
        elif response.status == 403:
            msg = (await response.json()).get("message", "")
            if "Out of call volume quota" in msg:
                raise CannotConnect(f"API rate limit exceeded: {msg}")
            else:
                raise CannotConnect("unknown")
        elif response.status == 429:
            msg = (await response.json()).get("message", "")
            raise CannotConnect(f"API rate limit exceeded: {msg}")
        else:
            raise CannotConnect("unknown")

    async def filter_river_stations(self, response) -> List[Dict[str, Any]]:
        """Filters the list of stations from NRW for rivers only"""
        station_key = "titleEn"
        stations = []

        for station in response:
            river_level_param = next(
                (
                    p["parameter"]
                    for p in station.get("parameters", [])
                    if p.get("paramNameEN") == RIVER_LEVEL
                ),
                None,
            )
            if river_level_param:
                stations.append(
                    {
                        "title": station[station_key],
                        "id": station["stationId"],
                        "river_level_param": river_level_param
                    }
                )

        stations = sorted(stations, key=lambda x: x["title"])
        return stations

    async def async_step_user(self, user_input=None):
        """The initial form when setting the integration up"""
        return self.async_show_menu(
            step_id="user",
            menu_options=self.get_initial_menu_options()
        )

    async def async_step_floodalert(self, user_input=None):
        """The form to setup flood alert section of integration"""
        return self.async_abort(reason="feature_not_implemented")

    async def async_step_riverlevel(self, user_input=None):
        """Chooses whether to show API connection/river select form"""
        try:
            if self.api_key is None:
                for entry in self.hass.config_entries.async_entries(DOMAIN):
                    if "stations" in entry.data:
                        self.api_key = entry.data["api_key"]
                        stations = await self.fetch_station_data(self.api_key)
                        schema = self.get_river_list_schema(stations)
                        return self.async_show_form(
                            step_id="select_station",
                            data_schema=schema
                        )
            schema = self.get_api_schema()
            return self.async_show_form(
                step_id="add_river_api",
                data_schema=schema
            )
        except Exception as e:
            _LOGGER.warning(
                f"Error during config flow setup: {str(e)}"
            )
            return self.async_abort(reason="config_flow_failed")

    async def async_step_add_river_api(self, user_input=None):
        """Form where the user adds the river API connection"""
        if user_input is not None:
            try:
                stations = await self.fetch_station_data(
                    user_input["api_key"]
                )
                schema = self.get_river_list_schema(stations)
                return self.async_show_form(
                    step_id="select_station",
                    data_schema=schema
                )
            except Exception as e:
                errors = {"base": str(e)}
                schema = self.get_api_schema()
                return self.async_show_form(
                    step_id="add_river_api",
                    data_schema=schema,
                    errors=errors
                )

    async def async_step_select_station(self, user_input=None):
        """Form where the user selects the river station to monitor"""
        if user_input is not None:
            try:
                station = int(
                    user_input["station"].split(" (")[-1].rstrip(")")
                )
                current_entries = self._async_current_entries()

                for entry in current_entries:
                    if entry.data.get("api_key") == self.api_key:
                        new_stations = list(entry.data.get("stations", []))
                        if station not in new_stations:
                            new_stations.append(station)
                        new_data = {**entry.data, "stations": new_stations}
                        return self.async_update_reload_and_abort(
                            entry,
                            data=new_data,
                            reason="additional_station_added"
                        )

                new_data = {
                    "api_key": self.api_key,
                    "stations": [station]
                }
                return self.async_create_entry(
                    title=f"River Levels ({self.api_key[-5:]})",
                    data=new_data,
                )
            except Exception as e:
                _LOGGER.warning(
                    f"Error during config flow setup: {str(e)}"
                )
                return self.async_abort(reason="config_flow_failed")

    async def async_step_reauth(
        self,
        entry_data: Mapping[str, Any],
    ) -> ConfigFlowResult:
        """Sends to reauth form when the API key no longer valid"""

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handles reauthentication when API key no longer valid"""

        self._get_reauth_entry()
        entry = self._get_reauth_entry()

        schema = vol.Schema(
            {
                vol.Required("api_key"): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.PASSWORD
                    )
                )
            })

        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=schema
            )

        self.api_key = user_input["api_key"]

        session = async_get_clientsession(self.hass)

        try:
            async with session.get(
                f"{API_BASE_URL}{API_STATIONDATA_EP}",
                headers={"Ocp-Apim-Subscription-Key": self.api_key},
            ) as response:
                if response.status == 200:
                    entry = self._get_reauth_entry()
                    updated_data = {**entry.data, "api_key": self.api_key}
                    self.async_update_reload_and_abort(
                        entry,
                        data=updated_data,
                        title=f"River Levels ({self.api_key[-5:]})",
                    )
                    return self.async_abort(reason="reauth_successful")
                elif response.status == 401:
                    raise InvalidAuth("invalid_auth")
                else:
                    raise CannotConnect("unknown")

        except Exception as e:
            errors = {"base": str(e)}
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=schema,
                errors=errors,
            )
