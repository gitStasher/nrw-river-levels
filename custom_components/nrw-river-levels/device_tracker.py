from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL
from homeassistant.components.device_tracker import TrackerEntity, SourceType
from .coordinator import NaturalResourcesWalesCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []
    for station_id in entry.data.get("stations", []):
        entities.append(StationDeviceTracker(coordinator, station_id))
    async_add_entities(entities)

class StationDeviceTracker(
    CoordinatorEntity[NaturalResourcesWalesCoordinator],
    TrackerEntity):
    def __init__(
        self,
        coordinator: NaturalResourcesWalesCoordinator,
        station_id: int,
        ) -> None:
            super().__init__(coordinator)
            self.station_id = station_id

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.station_id}_device_tracker"

    @property
    def name(self):
        return "Station Location"

    @property
    def latitude(self):
        coords = self.coordinator.data["stations"][self.station_id].get(
            "coordinates", {}
        )
        return coords.get("latitude")

    @property
    def longitude(self):
        coords = self.coordinator.data["stations"][self.station_id].get(
            "coordinates", {}
        )
        return coords.get("longitude")

    @property
    def source_type(self):
        return SourceType.GPS

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self.station_id)},
            "name": (
                self.coordinator.data["stations"][self.station_id]["titleEn"]
            ),
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL
        }
