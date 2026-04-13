from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL
from homeassistant.components.device_tracker import TrackerEntity, SourceType
from .coordinator import NaturalResourcesWalesCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []
    entities.append(StationDeviceTracker(coordinator))
    async_add_entities(entities)

class StationDeviceTracker(CoordinatorEntity[NaturalResourcesWalesCoordinator], TrackerEntity):
    def __init__(self, coordinator: NaturalResourcesWalesCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.coordinator.stationId}_device_tracker"

    @property
    def name(self):
        return "Station Location"

    @property
    def latitude(self):
        coordinates = self.coordinator.data.get("coordinates", {})
        return coordinates.get("latitude")

    @property
    def longitude(self):
        coordinates = self.coordinator.data.get("coordinates", {})
        return coordinates.get("longitude")

    @property
    def source_type(self):
        return SourceType.GPS

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.stationId)},
            "name": self.coordinator.station,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL
        }
