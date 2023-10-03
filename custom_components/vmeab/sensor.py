"""Platform for sensor integration."""
from __future__ import annotations
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from datetime import datetime
from .datumOmvandlare import omvandlaTillDatetime, dagarTillDatum
import json
from .const import (
    DOMAIN,
    DEVICE_NAME,
)
from pathlib import Path

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import (
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


async def async_setup_entry(
    hass: HomeAssistant, config_entry, async_add_entities: AddEntitiesCallback
) -> None:
    # tunnor = Trash.fetchData(hass)

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    tunnor = coordinator.tunnor

    entities = []
    # Hittar alla olika typer av tunnor som finns.
    for tunna, hamtning in tunnor.items():
        if tunna == "last_update":
            continue
        entities.append(Trashcan(hass, coordinator, tunna, hamtning))

    entities.append(
        NextTrashCan(hass, coordinator)
    )  # Lägger till alla tunnorna i denna array

    async_add_entities(entities)  # Skapar själva entities baserat på array'n


class Trash(CoordinatorEntity, SensorEntity):
    def __init__(
        self, hass: HomeAssistant, coordinator: DataUpdateCoordinator, name, state
    ) -> None:
        super().__init__(coordinator)
        self._attr_icon = "mdi:trash-can"
        self._attr_native_value = state
        self._name = name
        self._attr_unique_id = "VMEAB " + name
        self._hass = hass
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, DEVICE_NAME)},
            ATTR_NAME: DEVICE_NAME,
            ATTR_MANUFACTURER: "@nightcbis",
        }

    def update(self) -> None:
        """Används ej"""

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> str:
        return self._attr_native_value

    @property
    def device_class(self):
        return f"{DOMAIN}__providersensor"


class Trashcan(Trash):
    """En specifik tunna"""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: DataUpdateCoordinator,
        name,
        tunna,
    ) -> None:
        # hass, coordinator, name, state
        super().__init__(hass, coordinator, name, tunna)
        self._coordinator = coordinator
        self._attr_extra_state_attributes = self.attributes()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Den här funktionen körs när coordinator kör sin uppdatering"""

        # Hämtar ny data
        tunnor = self._coordinator.tunnor

        self._attr_native_value = tunnor[self._name]
        self._attr_extra_state_attributes = self.attributes()
        self.async_write_ha_state()  # Måste köras för att HA ska förstå att vi uppdaterat allt klart.

    def attributes(self):
        """Funktion för att fixa attributes så det slipper ligga dubbelt i __init__ samt _handle_coordinator_update"""
        return {
            "Datetime": omvandlaTillDatetime(self._attr_native_value),
            "Veckodag": self._attr_native_value.split(" ")[0],
            "Dagar": dagarTillDatum(self._attr_native_value),
            "Uppdaterad": datetime.now(),
            "friendly_name": self._name,
        }


class NextTrashCan(Trash):
    """En sensor som säger vilken tunna som hämtas här näst"""

    # Letar reda på tunnan i tunnor-listan

    def __init__(self, hass: HomeAssistant, coordinator) -> None:
        self._name = "Next Pickup"
        self._coordinator = coordinator

        # Hämtar rätt tunna till "tunna"
        tunnor = self._coordinator.tunnor

        # tunnor = Trash.fetchData(hass)
        tunna = self.hittaTunna(tunnor)

        # Hass, coordinator, name, state
        super().__init__(hass, coordinator, self._name, tunna)

        self._attr_extra_state_attributes = self.attributes(tunnor, tunna)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Den här funktionen körs när coordinator kör sin uppdatering"""
        # Hämtar tunnan
        tunnor = self._coordinator.tunnor
        # tunnor = Trash.fetchData(self._hass)
        nastaTunna = self.hittaTunna(tunnor)

        self._attr_native_value = nastaTunna
        self._attr_extra_state_attributes = self.attributes(tunnor, nastaTunna)

        self.async_write_ha_state()  # Säger till HA att uppdatera

    def attributes(self, tunnor, nastaTunna):
        """Funktion för att fixa attributes så det slipper ligga dubbelt i __init__ samt _handle_coordinator_update"""
        return {
            "Datetime": omvandlaTillDatetime(tunnor[nastaTunna]),
            "Veckodag": tunnor[nastaTunna].split(" ")[0],
            "Dagar": dagarTillDatum(tunnor[nastaTunna]),
            "Rentext": f"{self._attr_native_value} om {str(dagarTillDatum(tunnor[nastaTunna]))} dagar",
            "Hämtning": tunnor[nastaTunna],
            "Uppdaterad": datetime.now(),
            "friendly_name": self._name,
        }

    @staticmethod
    def hittaTunna(tunnor):
        """Den här funktionen hittar vilken tunna som är nästa tunna att hämtas."""
        tunnorArray = {}
        for tunna, hamtning in tunnor.items():
            if tunna == "last_update":
                continue
            tunnorArray[tunna] = dagarTillDatum(hamtning)

        return min(
            tunnorArray, key=tunnorArray.get
        )  # Retunerar bara den tunna med lägst antal dagar till hämtning
