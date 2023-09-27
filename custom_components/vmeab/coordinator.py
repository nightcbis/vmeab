import logging
import aiohttp
import json
import time

from pathlib import Path
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant
from bs4 import BeautifulSoup
from .const import DOMAIN, CONFIG_FILE, CONF_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_get_page(vmeab, URL):
    async with vmeab.get(URL) as page:
        text = await page.read()

    return BeautifulSoup(text, "html.parser")


async def async_post_page(vmeab, URL, data):
    async with vmeab.post(URL, data=data) as page:
        text = await page.read()

    return BeautifulSoup(text, "html.parser")


def saveFile(hass: HomeAssistant, tunnor):
    jsonFilePath = Path(hass.config.path(CONFIG_FILE))
    jsonFilePath.touch(exist_ok=True)

    jsonFile = open(jsonFilePath, "w", encoding="utf-8")
    jsonFile.write(json.dumps(tunnor, indent=4))

    jsonFile.close()


class MyCoordinator(DataUpdateCoordinator):
    """Coordinator som uppdaterar datan vi har"""

    def __init__(self, hass: HomeAssistant, my_api, StreetName, City) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="VMEAB Coordinator",
            update_interval=CONF_UPDATE_INTERVAL,
        )
        self.my_api = my_api
        self._street = StreetName
        self._city = City
        self._hass = hass

    async def _async_update_data(self):
        """Fetcha infon här."""
        # tunnor = vmeab_scrape("Flundregatan 29", "Västervik")

        URL = "https://www.vmeab.se/tjanster/avfall--atervinning/min-sophamtning/"
        HOSTURL = "https://www.vmeab.se"

        vmeab = aiohttp.ClientSession()
        soup = await async_get_page(vmeab, URL)

        # Hittar formen för sökningen. Vi måste plocka ur en dold nyckel där med mera.
        form = soup.find(id="wasteDisposalNextPickupForm")

        # VMEAB har skapat en dold input som innehåller en nyckel som vi måste skicka i våran post.
        # Detta är för att hämta den.
        __RequestVerificationToken = form.find(type="hidden")["value"]

        # Ifall att de ändrar var API't ligger så hämtar vi den här varje gång.
        formAction = form["action"]
        formURL = HOSTURL + formAction

        # Detta är våran data för våran post
        data = {
            "__RequestVerificationToken": __RequestVerificationToken,
            "StreetAddress": self._street,
            "City": self._city,
        }

        soup = await async_post_page(vmeab, formURL, data)
        await vmeab.close()

        # Varje tunna ligger som en egen div med class waste-disposal-search-result-item
        allaTunnor = soup.find_all("div", class_="waste-disposal-search-result-item")

        tunnor = {}  # Använder json för att spara sakerna i.

        for tunna in allaTunnor:
            soup = BeautifulSoup(tunna.prettify(), "html.parser")

            # Lägger in varje träff som ett nytt inlägg i form av json
            tunnor[soup.find("h4").get_text().strip().split(",")[0]] = (
                soup.find("p").get_text().strip().split(": ")[1]
            )

        tunnor["last_update"] = time.time()
        saveFile(self._hass, tunnor)  # Spara ner resultatet
