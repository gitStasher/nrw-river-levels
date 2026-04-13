from homeassistant import config_entries
import aiohttp
import voluptuous as vol
from .const import DOMAIN, API_BASE_URL, API_STATIONDATA_EP, RIVER_LEVEL
from homeassistant.helpers import selector, translation

class NaturalResourcesWalesRiverLevelsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):       

    VERSION = 1

    def __init__(self):
        
        self.apiKey = None

    async def async_step_user(self, user_input=None):
        
        schema = vol.Schema(
                {
                    vol.Required("apiKey"): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                            )
                        )
                })

        if user_input is None:
            
            return self.async_show_form(step_id="user",
            data_schema=schema
            )

        try:

            errors = {}
            self.apiKey = user_input["apiKey"]
            
            async with aiohttp.ClientSession() as session:
                
                headers = {"Ocp-Apim-Subscription-Key": self.apiKey}
                
                async with session.get(API_BASE_URL + API_STATIONDATA_EP, headers=headers) as response:
                    
                    if response.status == 200:
                        
                        stationData = await response.json()
                    
                    elif response.status == 401:
                        
                        raise ValueError("invalid_auth")
                    
                    else:
                        
                        raise Exception("unknown")

                stationKey = "titleCy" if self.hass.config.language == "cy" else "titleEn"
                stations = []
                self.stationMap = {}

                for station in stationData:

                    riverLevelParam = next((p["parameter"] for p in station.get("parameters", []) if p.get("paramNameEN") == RIVER_LEVEL), None)
                    
                    if riverLevelParam:
                        
                        stations.append({"title": station[stationKey], "id": station["stationId"], "riverLevelParam": riverLevelParam}) 
                        stations = sorted(stations, key=lambda x: x["title"])
                        self.stationMap[station[stationKey]] = {
                                "id": station["stationId"],
                                "riverLevelParam": riverLevelParam
                                }
                
                options = [station["title"] for station in stations]
                schema = vol.Schema(
                        {
                            vol.Required("station"): vol.In(options)
                            }
                        )

                return self.async_show_form(step_id="select_station", data_schema=schema)

        except Exception as e:

            errors = {"base": str(e)}
            return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_select_station(self, user_input):

        station = user_input["station"]
        stationId = self.stationMap[station]["id"]
        riverLevelParam = self.stationMap[station]["riverLevelParam"]

        return self.async_create_entry(
                title=station,
                data={"apiKey": self.apiKey, "station": station, "stationId": stationId, "riverLevelParam": riverLevelParam})

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:

        self._get_reauth_entry()
        entry = self._get_reauth_entry()

        schema = vol.Schema(
                {
                    vol.Required("apiKey"): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                            )
                        )
                    })

        if user_input is None:
            return self.async_show_form(
                    step_id="reauth_confirm",
                    data_schema=schema)

        self.apiKey = user_input["apiKey"]

        async with aiohttp.ClientSession() as session:

            headers = {"Ocp-Apim-Subscription-Key": self.apiKey}
            
            try:
                
                async with session.get(API_BASE_URL + API_STATIONDATA_EP, headers=headers) as response:
                    
                    errors = {}
                    
                    if response.status == 200:
                        entry = self._get_reauth_entry()
                        updated_data = {**entry.data, "apiKey": self.apiKey}
                        self.async_update_reload_and_abort(entry, data=updated_data)
                        return self.async_abort(reason="reauth_successful")
                    elif response.status == 401:
                        raise ValueError("invalid_auth")
                    else:
                        raise Exception("unknown")
            
            except Exception as e:
                
                errors = {"base": str(e)}
                return self.async_show_form(step_id="reauth_confirm", data_schema=schema, errors=errors)
