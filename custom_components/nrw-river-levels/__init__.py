from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from homeassistant.const import Platform
from .coordinator import NaturalResourcesWalesCoordinator
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    _LOGGER.info("Setting up Natural Resources Wales integration for entry: %s", entry.entry_id)
    coordinator = NaturalResourcesWalesCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}
    
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.DEVICE_TRACKER])

    return True
