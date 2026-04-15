from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass
)
from .coordinator import NaturalResourcesWalesCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []
    for station_id in entry.data.get("stations", []):
        entities.append(StationStatusSensor(coordinator, station_id))
    async_add_entities(entities)

class StationStatusSensor(
    CoordinatorEntity[NaturalResourcesWalesCoordinator],
    BinarySensorEntity
):
    def __init__(
        self,
        coordinator: NaturalResourcesWalesCoordinator,
        station_id: int,
    ) -> None:
        super().__init__(coordinator)
        self._attr_device_class = BinarySensorDeviceClass.RUNNING
        self.station_id = station_id

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.station_id}_station_status"

    @property
    def name(self):
        return "Station Status"

    @property
    def is_on(self):
        return self.coordinator.data["stations"][self.station_id].get(
            "statusEN"
        ) == "Online"

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
