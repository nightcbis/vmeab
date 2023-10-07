"""Platform for text"""
from __future__ import annotations
from pathlib import Path
from homeassistant.components.text import TextEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_IDENTIFIERS, ATTR_MANUFACTURER, ATTR_NAME
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from .const import DOMAIN, DEVICE_NAME, CONF_FILE
import json


async def async_setup_entry(
    hass: HomeAssistant, config_entry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    tunnor = coordinator.tunnor

    entities = []
    for tunna, _ in tunnor.items():
        if tunna == "last_update":
            continue
        entities.append(Texter(hass, coordinator, tunna))

    async_add_entities(entities)


class Texter(CoordinatorEntity, TextEntity):
    def __init__(
        self, hass: HomeAssistant, coordinator: DataUpdateCoordinator, name
    ) -> None:
        super().__init__(coordinator)
        self._name = name
        self._attr_unique_id = name
        self._hass = hass
        self._coordinator = coordinator

        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, DEVICE_NAME)},
            ATTR_NAME: DEVICE_NAME,
            ATTR_MANUFACTURER: "@nightcbis",
        }
        self._attr_has_entity_name = True

        smeknamn = self.readConfig()

        self._coordinator.smeknamn[self._name] = smeknamn
        self._attr_native_value = smeknamn

    def writeConfig(self, smeknamn) -> None:
        path = self._hass.config.path(CONF_FILE)
        configFile = Path(path)
        configFile.touch(exist_ok=True)

        with open(path, "r", encoding="utf-8") as configFile:
            try:
                data = json.loads(configFile.read())
            except:
                data = {}

        data[self._name] = smeknamn
        self._coordinator.smeknamn[self._name] = smeknamn

        with open(path, "w", encoding="utf-8") as configFile:
            configFile.write(json.dumps(data, indent=4))

    def readConfig(self, tunna="NAME"):
        if tunna == "NAME":
            tunna = self._name

        path = self._hass.config.path(CONF_FILE)
        configFile = Path(path)
        configFile.touch(exist_ok=True)

        with open(path, "r", encoding="utf-8") as configFile:
            data = json.loads(configFile.read())

        try:
            smeknamn = data[tunna]
        except:
            self.writeConfig(tunna, tunna)
            smeknamn = tunna

        return smeknamn

    def update(self) -> None:
        """Används ej"""

    async def async_set_value(self, value: str) -> None:
        """Set value"""
        self._attr_native_value = value
        self.writeConfig(value)
        self.async_schedule_update_ha_state(force_refresh=False)

    @property
    def native_value(self) -> str | None:
        return self._attr_native_value

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def unique_id(self) -> str | None:
        return super().unique_id

    @property
    def state(self) -> str | None:
        return self._attr_native_value

    @property
    def device_class(self) -> str | None:
        return super().device_class
