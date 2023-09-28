"""Platform for sensor integration."""
from __future__ import annotations

from .datumOmvandlare import omvandlaTillDatetime, dagarTillDatum
import time
import json
from .const import (
    CONF_SENSOR_UPDATE_INTERVAL,
    CONF_CITY,
    CONF_STREET,
    DOMAIN,
    CONFIG_FILE,
    DEVICE_NAME,
)
from pathlib import Path

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
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
    # _city = config[CONF_CITY]
    # _street = config[CONF_STREET]
    _city = config_entry.data.get(CONF_CITY)
    _street = config_entry.data.get(CONF_STREET)
    tunnor = fetchData(hass, _street, _city)

    entities = []
    for tunna, hamtning in tunnor.items():
        if tunna == "last_update":
            continue

        entities.append(Trashcan(hass, tunna, hamtning, _street, _city))

    entities.append(NextTrashCan(hass, _street, _city))

    async_add_entities(entities)


def fetchData(
    hass: HomeAssistant, street, city
):  # Måste fixa så den inte kraschar om den körs utan json-filen
    tunnor = {}
    # Skapar filen om den inte finns
    jsonFilePath = Path(hass.config.path(CONFIG_FILE))
    jsonFilePath.touch(exist_ok=True)

    jsonFile = open(jsonFilePath, "r", encoding="utf-8")
    jsonFileData = jsonFile.read()
    jsonFile.close()

    last_update = time.time()
    firstRun = False

    # Kollar om vi har skapat filen tidigare
    try:
        jsonFileData = json.loads(jsonFileData)
        last_update = jsonFileData["last_update"]
    except:
        firstRun = True

    # Vi behöver göra en scrape från VMEAB
    #    if firstRun == True or (time.time() - last_update > CONF_SENSOR_UPDATE_INTERVAL):
    #       last_update = time.time()

    # tunnor = vmeab_scrape(street, city)
    #       tunnor["last_update"] = last_update

    #        jsonFile = open(jsonFilePath, "w", encoding="utf-8")
    #       jsonFile.write(json.dumps(tunnor, indent=4))
    #       jsonFile.close()

    # print("Fetched new info from VMEAB:" + str(tunnor))
    #      return tunnor

    # Vi behövde inte hämta ifrån VMEAB så vi tar ifrån datan vi redan har ifrån filen.
    tunnor = jsonFileData
    # print("Fetched from file: " + str(tunnor))

    return tunnor


class Trashcan(SensorEntity):
    """En specifik tunna"""

    def __init__(self, hass: HomeAssistant, name, hamtning, street, city) -> None:
        self._attr_native_value = hamtning
        self._name = name
        self._attr_unique_id = name
        self._attr_icon = "mdi:trash-can"
        self._last_update = time.time()
        self._update_interval = (
            CONF_SENSOR_UPDATE_INTERVAL  # Hur ofta vi kollar mot vmeab
        )
        self._city = city
        self._street = street
        self._test_nummer = 1
        self._update_sensor_interval = CONF_SENSOR_UPDATE_INTERVAL  # Uppdaterar bara sensorn en gång i timmen. Slipper öppna filen så ofta då.
        self._hass = hass
        self._attr_extra_state_attributes = {
            "Datetime": omvandlaTillDatetime(self._attr_native_value),
            "Veckodag": self._attr_native_value.split(" ")[0],
            "Dagar": dagarTillDatum(self._attr_native_value),
        }
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, DEVICE_NAME)},
            ATTR_NAME: DEVICE_NAME,
            ATTR_MANUFACTURER: "@nightcbis",
        }

    def update(self) -> None:
        """Updating"""
        # Behöver vi ens uppdatera oss?
        if time.time() - self._last_update > int(self._update_sensor_interval):
            # Hämtar ny data
            tunnor = fetchData(self._hass, self._street, self._city)

            # Uppdaterar
            self._attr_native_value = tunnor[self._name]
            self._attr_extra_state_attributes = {
                "Datetime": omvandlaTillDatetime(self._attr_native_value),
                "Veckodag": self._attr_native_value.split(" ")[0],
                "Dagar": dagarTillDatum(self._attr_native_value),
            }
            self._last_update = time.time()

    @property
    def name(self) -> str:
        return "VMEAB " + self._name

    @property
    def state(self) -> str:
        return self._attr_native_value

    @property
    def device_class(self):
        return f"{DOMAIN}__providersensor"


def hittaTunna(tunnor):
    tunnorArray = {}
    for tunna, hamtning in tunnor.items():
        if tunna == "last_update":
            continue
        tunnorArray[tunna] = dagarTillDatum(hamtning)

    # print(tunnorArray)
    # print(f"Min:[{min(tunnorArray, key=tunnorArray.get)}] {min(tunnorArray.values())}")

    return min(tunnorArray, key=tunnorArray.get)


class NextTrashCan(SensorEntity):
    """En sensor som säger vilken tunna som hämtas här näst"""

    def __init__(self, hass: HomeAssistant, street, city) -> None:
        self._name = "VMEAB Next Pickup"
        self._attr_unique_id = self._name
        self._attr_icon = "mdi:trash-can"
        self._hass = hass
        self._street = street
        self._city = city
        self._update_interval = (
            CONF_SENSOR_UPDATE_INTERVAL  # Hur ofta vi kollar mot vmeab
        )
        self._last_update = time.time()
        self._update_sensor_interval = (
            60  # Den här kollar vi en gång i minuten för att det ska synka bra.
        )
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, DEVICE_NAME)},
            ATTR_NAME: DEVICE_NAME,
            ATTR_MANUFACTURER: "@nightcbis",
        }

        # Hämtar rätt tunna till "tunna"
        tunnor = fetchData(self._hass, self._street, self._city)
        tunna = hittaTunna(tunnor)

        self._attr_native_value = tunna
        # print(tunna)
        self._attr_extra_state_attributes = {
            "Datetime": omvandlaTillDatetime(tunnor[self._attr_native_value]),
            "Veckodag": tunnor[self._attr_native_value].split(" ")[0],
            "Dagar": dagarTillDatum(tunnor[self._attr_native_value]),
            "Rentext": self._attr_native_value
            + " om "
            + str(dagarTillDatum(tunnor[self._attr_native_value]))
            + " dagar",
            "Hämtning": tunnor[tunna],
        }

    def update(self) -> None:
        # Behöver vi ens uppdatera oss?
        if time.time() - self._last_update > int(self._update_sensor_interval):
            # Hämtar tunnan
            tunnor = fetchData(self._hass, self._street, self._city)
            tunna = hittaTunna(tunnor)

            # uppdaterar
            self._attr_native_value = tunna
            self._attr_extra_state_attributes = {
                "Datetime": omvandlaTillDatetime(tunnor[self._attr_native_value]),
                "Veckodag": tunnor[self._attr_native_value].split(" ")[0],
                "Dagar": dagarTillDatum(tunnor[self._attr_native_value]),
                "Rentext": self._attr_native_value
                + " om "
                + str(dagarTillDatum(tunnor[self._attr_native_value]))
                + " dagar",
                "Hämtning": tunnor[tunna],
            }

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> str:
        return self._attr_native_value
