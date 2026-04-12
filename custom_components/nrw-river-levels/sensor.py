from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from .coordinator import NaturalResourcesWalesCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfLength
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    await coordinator.async_config_entry_first_refresh()
    entities: list[SensorEntity] = []
    
    entities.append(RiverLevelSensor(coordinator))
    async_add_entities(entities)
    
class RiverLevelSensor(CoordinatorEntity[NaturalResourcesWalesCoordinator], SensorEntity):

    def __init__(self, coordinator: NaturalResourcesWalesCoordinator) -> None:

            super().__init__(coordinator)
            self._attr_device_class = SensorDeviceClass.DISTANCE
            self._attr_native_unit_of_measurement = UnitOfLength.METERS

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.coordinator.stationId}_river_level"

    @property
    def name(self):
        return "River Level"

    @property
    def native_value(self):
        readings = self.coordinator.data.get("parameterReadings", [])
        if not readings:
            return None
        return float(readings[-1]["value"]) if readings else None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.stationId)},
            "name": self.coordinator.station,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL
        }
