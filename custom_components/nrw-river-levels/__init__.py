from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from homeassistant.const import Platform
from .coordinator import NaturalResourcesWalesCoordinator
import logging

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
        Platform.SENSOR,
        Platform.BINARY_SENSOR,
        Platform.DEVICE_TRACKER
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    _LOGGER.info(
        "Setting up Natural Resources Wales integration for entry: %s.",
        entry.entry_id
    )
    coordinator = NaturalResourcesWalesCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS
    )
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

async def async_migrate_entry(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> bool:
    if config_entry.version == 1:
        data = {
            "api_key": config_entry.data["apiKey"],
            "stations": [config_entry.data["stationId"]],
        }
        title = f"River Levels ({data['api_key'][-5:]})"
        hass.config_entries.async_update_entry(
            config_entry,
            data=data,
            version=2,
            title=title
        )
    return True
