from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from .coordinator import NaturalResourcesWalesCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    await coordinator.async_config_entry_first_refresh()
    entities = []
    entities.append(StationStatusSensor(coordinator))
    async_add_entities(entities)

class StationStatusSensor(CoordinatorEntity[NaturalResourcesWalesCoordinator], BinarySensorEntity):
    def __init__(self, coordinator: NaturalResourcesWalesCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_class = BinarySensorDeviceClass.RUNNING

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.coordinator.stationId}_station_status"

    @property
    def name(self):
        return "Station Status"

    @property
    def is_on(self):
        return self.coordinator.data.get("statusEN") == "Online"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.stationId)},
            "name": self.coordinator.station,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL
        }
