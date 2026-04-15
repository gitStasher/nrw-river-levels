from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass
)
from .coordinator import NaturalResourcesWalesCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfLength
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging
from datetime import datetime
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[SensorEntity] = []
    for station_id in entry.data.get("stations", []):
        entities.append(RiverLevelSensor(coordinator, station_id))
        entities.append(RiverLevelLastUpdatedSensor(coordinator, station_id))
    async_add_entities(entities)

class RiverLevelSensor(
    CoordinatorEntity[NaturalResourcesWalesCoordinator],
    SensorEntity):
    def __init__(
        self,
        coordinator: NaturalResourcesWalesCoordinator,
        station_id: int) -> None:
        super().__init__(coordinator)
        self._attr_device_class = SensorDeviceClass.DISTANCE
        self._attr_native_unit_of_measurement = UnitOfLength.METERS
        self.station_id = station_id

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.station_id}_river_level"

    @property
    def name(self):
        return "River Level"

    @property
    def native_value(self):
        params = self.coordinator.data["stations"][self.station_id].get(
            "parameters", []
        )
        param = params[0] if params else None
        return float(param["latestValue"]) if param else None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.station_id)},
            "name": (
                self.coordinator.data["stations"][self.station_id]["titleEn"]
            ),
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL
        }

class RiverLevelLastUpdatedSensor(
    CoordinatorEntity[NaturalResourcesWalesCoordinator],
    SensorEntity,
):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: NaturalResourcesWalesCoordinator,
        station_id: int
    ) -> None:
        super().__init__(coordinator)
        self.station_id = station_id

    @property
    def unique_id(self) -> str:
        return (
            f"{DOMAIN}_{self.station_id}_river_level_last_updated"
        )

    @property
    def name(self) -> str:
        return "River Level Last Updated"

    @property
    def native_value(self):
        params = self.coordinator.data["stations"][self.station_id].get(
            "parameters", []
        )
        param = params[0] if params else None
        if not param:
            return None
        time_str = param.get("latestTime")
        if not time_str:
            return None
        try:
            return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        except Exception:
            return None

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
