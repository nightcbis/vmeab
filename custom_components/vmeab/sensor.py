"""Platform for sensor integration."""
from __future__ import annotations

from .scraper import vmeab_scrape
import time
import json
from pathlib import Path

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

DOMAIN = "vmeab"


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    dicovery_info: DiscoveryInfoType | None = None,
) -> None:
    _city = config["city"]
    _street = config["street"]
    _update_interval = config["update_interval"]

    print("START!")

    tunnor = fetchData(_street, _city, _update_interval)

    for tunna, hamtning in tunnor.items():
        if tunna == "last_update":
            continue
        add_entities([Trashcan(tunna, hamtning, _street, _city, _update_interval)])


def fetchData(street, city, update_interval):
    tunnor = {}
    # Skapar filen om den inte finns
    jsonFilePath = Path("config/vmeab.json")
    jsonFilePath.touch(exist_ok=True)

    jsonFile = open(jsonFilePath, "r")
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
    if firstRun == True or (time.time() - last_update > update_interval):
        last_update = time.time()

        tunnor = vmeab_scrape(street, city)
        tunnor["last_update"] = last_update

        jsonFile = open(jsonFilePath, "w")
        jsonFile.write(json.dumps(tunnor, indent=4))
        jsonFile.close()

        print("Fetched new info from VMEAB:" + str(tunnor))
        return tunnor

    # Vi behövde inte hämta ifrån VMEAB så vi tar ifrån datan vi redan har ifrån filen.
    tunnor = jsonFileData
    print("Fetched from file: " + str(tunnor))

    return tunnor


class Trashcan(SensorEntity):
    """En specifik tunna"""

    def __init__(self, name, hamtning, street, city, update_interval) -> None:
        self._attr_native_value = hamtning
        self._name = name
        self._last_update = time.time()
        self._update_interval = update_interval
        self._city = city
        self._street = street
        self._test_nummer = 1
        self._update_sensor_interval = 3600  # Uppdaterar bara sensorn en gång i timmen. Slipper öppna filen så ofta då.

    @property
    def device_info(self) -> DeviceInfo | None:
        return super().device_info

    @property
    def name(self) -> str:
        return "VMEAB " + self._name

    @property
    def state(self) -> str:
        return self._attr_native_value

    def update(self) -> None:
        """Updating"""
        # Behöver vi ens uppdatera oss?
        if time.time() - self._last_update > self._update_sensor_interval:
            # Hämtar ny data
            tunnor = fetchData(self._street, self._city, self._update_interval)

            # Uppdaterar
            self._attr_native_value = tunnor[self._name]
            self._last_update = time.time()
