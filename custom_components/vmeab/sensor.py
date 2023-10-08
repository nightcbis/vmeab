"""Platform for sensor integration."""
from __future__ import annotations
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from datetime import datetime
from .datumOmvandlare import omvandlaTillDatetime, dagarTillDatum, svenskaTillEngelska
import json
from .const import (
    DOMAIN,
    DEVICE_NAME,
)

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
        self._attr_unique_id = name
        self._hass = hass

        self._attr_translation_key = "vmeab"
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, DEVICE_NAME)},
            ATTR_NAME: DEVICE_NAME,
            ATTR_MANUFACTURER: "@nightcbis",
        }
        self._attr_has_entity_name = True

    def update(self) -> None:
        """Används ej"""

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

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
        self._attr_native_value = dagarTillDatum(coordinator.tunnor[self._name])
        self._attr_extra_state_attributes = self.attributes(coordinator.tunnor)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Den här funktionen körs när coordinator kör sin uppdatering"""

        # Hämtar ny data
        tunnor = self._coordinator.tunnor

        self._attr_native_value = dagarTillDatum(tunnor[self._name])
        self._attr_extra_state_attributes = self.attributes(tunnor)
        self.async_write_ha_state()  # Måste köras för att HA ska förstå att vi uppdaterat allt klart.

    def attributes(self, tunnor):
        """Funktion för att fixa attributes så det slipper ligga dubbelt i __init__ samt _handle_coordinator_update"""
        return {
            "Hämtning": tunnor[self._name],
            "Datetime": omvandlaTillDatetime(tunnor[self._name]),
            "Veckodag": tunnor[self._name].split(" ")[0],
            "Dagar": dagarTillDatum(tunnor[self._name]),
            "Uppdaterad": datetime.now(),
        }


class NextTrashCan(Trash):
    """En sensor som säger vilken tunna som hämtas här näst"""

    def __init__(self, hass: HomeAssistant, coordinator) -> None:
        self._name = "Next Pickup"
        self._coordinator = coordinator

        # Hämtar rätt tunna till "tunna"
        tunnor = self._coordinator.tunnor

        # tunnor = Trash.fetchData(hass)
        tunna = self.hittaTunna(tunnor)

        # Hass, coordinator, name, state
        super().__init__(hass, coordinator, self._name, tunna)

        self._attr_native_value = self._coordinator.smeknamn[tunna]
        self._attr_extra_state_attributes = self.attributes(tunnor, tunna)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Den här funktionen körs när coordinator kör sin uppdatering"""
        # Hämtar tunnan
        tunnor = self._coordinator.tunnor
        # tunnor = Trash.fetchData(self._hass)
        nastaTunna = self.hittaTunna(tunnor)
        smeknamn = self._coordinator.smeknamn[nastaTunna]

        self._attr_native_value = smeknamn
        self._attr_extra_state_attributes = self.attributes(tunnor, nastaTunna)

        self.async_write_ha_state()  # Säger till HA att uppdatera

    def attributes(self, tunnor, nastaTunna):
        """Funktion för att fixa attributes så det slipper ligga dubbelt i __init__ samt _handle_coordinator_update"""
        # Hämtar smeknamn för tunnan.
        smeknamn = self._coordinator.smeknamn[nastaTunna]

        # Tisdag 10 oktober t.ex.
        hamtning = tunnor[nastaTunna]

        # Tar ut Tisdag ur "Tisdag 10 oktober" och gör till liten bokstav. Används i Template
        veckodag = hamtning.split(" ")[0].lower()

        # Omvandlar till engelska
        veckodagEngelska = svenskaTillEngelska(veckodag)

        # Räknar ut antal dagar till hämtning bara.
        antalDagarTillHamtning = str(dagarTillDatum(hamtning))

        # Sparar även ner i datetime ifall att vi vill matcha mot det i framtiden.
        hamtningSomDatetime = omvandlaTillDatetime(hamtning)

        # Hämtar ut veckodag här igen, men den här gången kör vi inte lower case. Den här presenteras som den är.
        veckodagHamtningArPa = hamtning.split(" ")[0]

        # Tid att visas som "Uppdaterad"
        uppdaterad = datetime.now()

        # Lite logik för att ändra "tisdag" till "imorgon" t.ex.

        addon = "på"
        addonEn = "on"
        if int(antalDagarTillHamtning) == 2:
            veckodag = "i övermorgon"
            addon = ""
        elif int(antalDagarTillHamtning) == 1:
            veckodag = "i morgon"
            veckodagEngelska = "tomorrow"
            addon = ""
            addonEn = ""
        elif int(antalDagarTillHamtning) == 0:
            veckodag = "i dag"
            veckodagEngelska = "today"
            addon = ""
            addonEn = ""

        return {
            "Template sv/siffror": f"{smeknamn} om {antalDagarTillHamtning} dagar",
            "Template en/numbers": f"{smeknamn} in {antalDagarTillHamtning} days",
            "Template sv/dag": f"{smeknamn} {addon} {veckodag}",
            "Template en/day": f"{smeknamn} {addonEn} {veckodagEngelska}",
            "Veckodag": veckodagHamtningArPa,
            "Dagar": f"{antalDagarTillHamtning}",
            "Datetime": hamtningSomDatetime,
            "Hämtning": hamtning,
            "Uppdaterad": uppdaterad,
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
