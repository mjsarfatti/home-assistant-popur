from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.exceptions import HomeAssistantError
from .api import PopurCommandError
from .const import DOMAIN
from .entity import PopurEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for dev_id in coordinator.data:
        device_static_info = coordinator.devices_map[dev_id]
        entities.extend([
            PopurSettingNumber(coordinator, device_static_info, "wait_time", 18, "Wait Time", "mdi:timer-sand", 2, 30, UnitOfTime.MINUTES),
            PopurSettingNumber(coordinator, device_static_info, "leveling", 5, "Leveling Passes", "mdi:layers-triple", 2, 5, None),
        ])
    async_add_entities(entities)

class PopurSettingNumber(PopurEntity, NumberEntity):
    def __init__(self, coordinator, device, key, pid, name, icon, minimum, maximum, unit):
        super().__init__(coordinator, device)
        self._key = key
        self._pid = pid
        self._attr_unique_id = f"{self._device_id}_{key}"
        self._attr_name = name
        self._attr_icon = icon
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = unit
        self._attr_mode = NumberMode.BOX

    @property
    def native_value(self):
        return self.coordinator.data.get(self._device_id, {}).get(self._key)

    async def async_set_native_value(self, value):
        try:
            await self.hass.async_add_executor_job(self.coordinator.api.set_property, self._device_id, self._pid, int(value))
        except PopurCommandError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
