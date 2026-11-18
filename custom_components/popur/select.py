from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from .api import PopurCommandError
from .const import DOMAIN
from .entity import PopurEntity

OPTIONS = ["Off", "Clock", "Cycles Today", "Funny", "Heart"]

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for dev_id in coordinator.data:
        device_static_info = coordinator.devices_map[dev_id]
        entities.append(PopurDisplaySelect(coordinator, device_static_info))
    async_add_entities(entities)

class PopurDisplaySelect(PopurEntity, SelectEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_display"
        self._attr_name = "Display"
        self._attr_icon = "mdi:monitor"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_options = OPTIONS

    @property
    def current_option(self):
        value = self.coordinator.data.get(self._device_id, {}).get("display")
        if type(value) is int and 1 <= value <= len(OPTIONS):
            return OPTIONS[value - 1]
        return None

    async def async_select_option(self, option):
        try:
            await self.hass.async_add_executor_job(self.coordinator.api.set_property, self._device_id, 17, OPTIONS.index(option) + 1)
        except PopurCommandError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
